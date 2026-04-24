from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Lana API"
    app_env: str = "production"
    app_host: str = "127.0.0.1"
    app_port: int = 8010
    app_base_url: str = "http://127.0.0.1:8010"

    comfy_base_url: str = "http://127.0.0.1:8188"
    comfy_output_dir: str = "C:/Carpuncle Cloud/LanaApp/ComfyUI/output"
    comfy_checkpoint: str = "v1-5-pruned-emaonly.safetensors"
    comfy_default_width: int = 512
    comfy_default_height: int = 512
    comfy_default_steps: int = 8
    comfy_default_cfg: float = 5.0
    comfy_default_sampler: str = "euler"
    comfy_default_scheduler: str = "normal"

    database_url: str = "sqlite:///C:/LanaRun/lana_stack.db"
    output_public_base: str = "/outputs"
    output_local_dir: str = "C:/LanaRun/exports"

    telegram_bot_token: str = ""
    telegram_allowed_user_ids: str = ""
    telegram_polling_enabled: bool = True

    site_public_url: str = "https://lana-ki.de"
    cors_origins: str = "https://lana-ki.de,http://localhost:4321,http://127.0.0.1:4321"

    @property
    def allowed_user_ids(self) -> List[int]:
        values: List[int] = []
        for item in self.telegram_allowed_user_ids.split(","):
            item = item.strip()
            if not item:
                continue
            try:
                values.append(int(item))
            except ValueError:
                continue
        return values

    @property
    def cors_origin_list(self) -> List[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
