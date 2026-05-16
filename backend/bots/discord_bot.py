from __future__ import annotations

import logging
from typing import Any

from backend.memory.manager import MemoryManager
from backend.router.agent_router import AgentRouter

LOGGER = logging.getLogger(__name__)


class DiscordBotService:
    def __init__(self, token: str, agent_router: AgentRouter, memory: MemoryManager) -> None:
        self.token = token
        self.agent_router = agent_router
        self.memory = memory

    def build_bot(self) -> Any:
        import discord
        from discord.ext import commands

        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix="/", intents=intents)

        @bot.command(name="status")
        async def status_command(ctx: commands.Context[Any]) -> None:
            await ctx.send(f"Lana Discord Bot online. Memory: {len(self.memory.recall('', limit=5))}")

        @bot.command(name="lana")
        async def lana_command(ctx: commands.Context[Any], *, prompt: str) -> None:
            result = await self.agent_router.route_chat(prompt)
            await ctx.send(result.reply)

        LOGGER.info("Discord-Bot konfiguriert.")
        return bot
