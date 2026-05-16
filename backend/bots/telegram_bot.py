from __future__ import annotations

import logging
from typing import Any

from backend.memory.manager import MemoryManager
from backend.router.agent_router import AgentRouter
from backend.router.comfyui import ComfyUIClient

LOGGER = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(
        self,
        token: str,
        admin_telegram_id: str,
        agent_router: AgentRouter,
        comfyui: ComfyUIClient,
        memory: MemoryManager,
    ) -> None:
        self.token = token
        self.admin_telegram_id = str(admin_telegram_id)
        self.agent_router = agent_router
        self.comfyui = comfyui
        self.memory = memory
        self.port = 8023

    def is_admin(self, telegram_user_id: int | str | None) -> bool:
        return str(telegram_user_id or "") == self.admin_telegram_id

    async def status_payload(self) -> dict[str, Any]:
        entries = self.memory.recall("", limit=5)
        return {
            "ok": True,
            "service": "telegram-bot",
            "recent_memory_entries": len(entries),
        }

    async def lana_payload(self, prompt: str) -> dict[str, Any]:
        result = await self.agent_router.route_chat(prompt)
        return result.model_dump(mode="json")

    async def comfyui_payload(self, workflow: dict[str, Any]) -> dict[str, Any]:
        return await self.comfyui.run_workflow(workflow, client_id="telegram-bot")

    async def memory_payload(self, query: str) -> dict[str, Any]:
        return {
            "query": query,
            "entries": [entry.model_dump(mode="json") for entry in self.memory.recall(query)],
        }

    def build_application(self) -> Any:
        from telegram.ext import ApplicationBuilder, CommandHandler

        async def status_command(update: Any, context: Any) -> None:
            await update.message.reply_text(str(await self.status_payload()))

        async def lana_command(update: Any, context: Any) -> None:
            if not self.is_admin(update.effective_user.id):
                await update.message.reply_text("Nicht autorisiert.")
                return
            prompt = " ".join(context.args).strip()
            await update.message.reply_text(str(await self.lana_payload(prompt)))

        async def comfyui_command(update: Any, context: Any) -> None:
            if not self.is_admin(update.effective_user.id):
                await update.message.reply_text("Nicht autorisiert.")
                return
            workflow = {"text": " ".join(context.args).strip(), "width": 512, "height": 512}
            await update.message.reply_text(str(await self.comfyui_payload(workflow)))

        async def memory_command(update: Any, context: Any) -> None:
            if not self.is_admin(update.effective_user.id):
                await update.message.reply_text("Nicht autorisiert.")
                return
            query = " ".join(context.args).strip()
            await update.message.reply_text(str(await self.memory_payload(query)))

        application = ApplicationBuilder().token(self.token).build()
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("lana", lana_command))
        application.add_handler(CommandHandler("comfyui", comfyui_command))
        application.add_handler(CommandHandler("memory", memory_command))
        LOGGER.info("Telegram-Bot-Applikation konfiguriert.")
        return application
