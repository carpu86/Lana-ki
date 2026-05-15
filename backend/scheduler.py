from __future__ import annotations

import logging
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.agents.companion_agent import CompanionAgent
from backend.memory.qdrant_client import LanaMemory

logger = logging.getLogger(__name__)

_memory = LanaMemory()
scheduler = AsyncIOScheduler()

# Mindest-Inaktivität in Sekunden bevor proaktive Nachricht gesendet wird
INACTIVE_THRESHOLD_S = 3600  # 1 Stunde


async def _check_proactive_messages() -> None:
    """Alle 30 Minuten: Prüfe aktive Girls und sende proaktive Nachrichten."""
    logger.info("[scheduler] Prüfe proaktive Nachrichten ...")
    try:
        client = _memory._get_client()
        if client is None:
            return

        collections = await client.get_collections()
        col_names = [c.name for c in collections.collections]

        for col_name in col_names:
            if not col_name.startswith("lana_") or not col_name.endswith("_messages"):
                continue
            parts = col_name[len("lana_"):-len("_messages")].split("_", 1)
            if len(parts) != 2:
                continue
            user_id, girl_id = parts

            recent = await _memory.get_recent(user_id, girl_id, n=1)
            if not recent:
                continue

            last_ts = recent[-1].timestamp
            inactive_s = time.time() - last_ts
            if inactive_s < INACTIVE_THRESHOLD_S:
                continue

            character = await _memory.get_character(user_id, girl_id)
            agent = CompanionAgent(user_id=user_id, girl_id=girl_id, character_sheet=character)
            agent._last_interaction = last_ts

            try:
                message = await agent.generate_proactive_message()
                await _memory.store_message(
                    user_id=user_id,
                    girl_id=girl_id,
                    role="assistant",
                    content=message,
                    metadata={"proactive": True},
                )
                logger.info(
                    "[scheduler] Proaktive Nachricht gespeichert: user=%s girl=%s",
                    user_id,
                    girl_id,
                )
            except Exception as exc:
                logger.warning(
                    "[scheduler] Proaktive Nachricht fehlgeschlagen: user=%s girl=%s: %s",
                    user_id,
                    girl_id,
                    exc,
                )
    except Exception as exc:
        logger.error("[scheduler] Fehler beim proaktiven Check: %s", exc)


def start_scheduler() -> None:
    scheduler.add_job(
        _check_proactive_messages,
        trigger=IntervalTrigger(minutes=30),
        id="proactive_messages",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[scheduler] APScheduler gestartet (Intervall: 30 Minuten).")
