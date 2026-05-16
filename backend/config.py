from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
LOGGER = logging.getLogger(__name__)


def load_environment() -> None:
    load_dotenv(REPO_ROOT / ".env", override=False)
    load_dotenv(BACKEND_DIR / ".env", override=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "lana-ki-orchestrator"
    service_version: str = "1.0.0"
    lana_root: str = r"C:\Carpuncle Cloud\Lana KI"
    lana_log_root: str = r"C:\Carpuncle Cloud\Lana KI\logs"
    lana_backup_root: str = r"C:\Carpuncle Cloud\Lana KI\_backups"
    lana_runtime_root: str = r"C:\Carpuncle Cloud\Lana KI\runtime"
    lana_audit_root: str = r"C:\Carpuncle Cloud\Lana KI\audit"
    sync_folder_path: str = "/home/carpu/LanaApp/sync"
    lana_node_name: str = "laptop-hub"
    lana_hub_ip: str = "100.67.27.13"
    lana_worker_ip: str = "100.110.207.22"
    lana_api_port: int = 8024
    telegram_bot_port: int = 8023
    lana_vision_port: int = 8080
    lana_lmstudio_url: str = "http://127.0.0.1:1234"
    lana_comfyui_url: str = "http://127.0.0.1:8188"
    lana_vision_url: str = "http://100.67.27.13:8080"
    lana_mcp_transport: str = "streamable-http"
    lana_mcp_public_endpoint: str = "https://gateway.lana-ki.de/mcp"
    lana_timeout_seconds: float = 30.0
    scheduler_interval_seconds: int = 60
    scheduler_snapshot_interval_hours: int = 24
    lana_gemini_model: str = "gemini-2.5-flash"
    gemini_api_key_ref: str = "GEMINI_API_KEY"
    openai_api_key_ref: str = "OPENAI_API_KEY"
    openai_base_url: str = "https://api.openai.com/v1/chat/completions"
    openai_model: str = "gpt-4.1-mini"
    mcp_bearer_token_ref: str = "MCP_BEARER_TOKEN"
    telegram_bot_token: str = ""
    admin_telegram_id: str = ""
    enable_shell_tools: bool = False
    enable_autonomous_shell: bool = False
    tailscale_ssh_user: str = "carpu"
    tailscale_nodes_json: str = Field(
        default='{"windows-master":"127.0.0.1","laptop-hub":"100.67.27.13","cloud-brain":"100.110.207.22"}',
        alias="TAILSCALE_NODES_JSON",
    )

    @property
    def runtime_root_path(self) -> Path:
        return Path(self.lana_runtime_root)

    @property
    def backup_root_path(self) -> Path:
        return Path(self.lana_backup_root)

    @property
    def log_root_path(self) -> Path:
        return Path(self.lana_log_root)

    @property
    def node_map(self) -> dict[str, str]:
        try:
            parsed = json.loads(self.tailscale_nodes_json)
        except json.JSONDecodeError as exc:
            raise ValueError("TAILSCALE_NODES_JSON muss valides JSON sein.") from exc
        return {str(key): str(value) for key, value in parsed.items()}

    def resolve_secret(self, env_name: str) -> str | None:
        env_name = (env_name or "").strip()
        if not env_name:
            return None
        value = os.getenv(env_name)
        return value.strip() if value else None

    def resolved_mcp_bearer_token(self) -> str | None:
        return self.resolve_secret(self.mcp_bearer_token_ref)

    def critical_issues(self) -> list[str]:
        issues: list[str] = []
        required_values: dict[str, Any] = {
            "LANA_LOG_ROOT": self.lana_log_root,
            "LANA_BACKUP_ROOT": self.lana_backup_root,
            "LANA_RUNTIME_ROOT": self.lana_runtime_root,
            "LANA_AUDIT_ROOT": self.lana_audit_root,
            "SYNC_FOLDER_PATH": self.sync_folder_path,
            "TELEGRAM_BOT_TOKEN": self.telegram_bot_token,
            "ADMIN_TELEGRAM_ID": self.admin_telegram_id,
            "LANA_MCP_TRANSPORT": self.lana_mcp_transport,
            "MCP_BEARER_TOKEN_REF": self.mcp_bearer_token_ref,
        }
        for key, value in required_values.items():
            if value in (None, "", []):
                issues.append(f"{key} fehlt oder ist leer.")
        if not self.resolved_mcp_bearer_token():
            issues.append(
                f"Bearer-Token aus Referenz {self.mcp_bearer_token_ref!r} fehlt in der Laufzeitumgebung."
            )
        return issues


def configure_logging(settings: Settings) -> None:
    settings.log_root_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_environment()
    settings = Settings()
    LOGGER.debug("Settings geladen für Node %s", settings.lana_node_name)
    return settings


def validate_required_settings(settings: Settings) -> None:
    issues = settings.critical_issues()
    if issues:
        message = "Startup-Validierung fehlgeschlagen: " + "; ".join(issues)
        raise RuntimeError(message)
