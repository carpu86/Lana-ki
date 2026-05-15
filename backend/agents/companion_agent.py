from __future__ import annotations

import logging
import time
from datetime import datetime
from enum import Enum

from backend.memory.character_store import CharacterSheet
from backend.services.intent_router import IntentRouter

logger = logging.getLogger(__name__)

_intent_router = IntentRouter()


class MoodState(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    MELANCHOLIC = "melancholic"
    EXCITED = "excited"
    DISTANT = "distant"


class CompanionAgent:
    """Autonomer KI-Companion-Agent für eine Girl-Instanz."""

    def __init__(
        self,
        user_id: str,
        girl_id: str,
        character_sheet: CharacterSheet | None = None,
    ) -> None:
        self.user_id = user_id
        self.girl_id = girl_id
        self.character_sheet = character_sheet
        self.mood: MoodState = MoodState.NEUTRAL
        self._last_interaction: float = time.time()

    def _build_system_prompt(self) -> str:
        if self.character_sheet:
            cs = self.character_sheet
            return (
                f"Du bist {cs.name}, {cs.age} Jahre alt.\n"
                f"Persönlichkeit: {cs.personality}\n"
                f"Aussehen: {cs.appearance}\n"
                f"Aktuelle Stimmung: {self.mood.value}\n"
                f"Aktuelle Uhrzeit: {datetime.now().strftime('%H:%M')}\n"
                "Antworte natürlich und bleib in deiner Rolle."
            )
        return (
            f"Du bist ein KI-Companion mit der ID '{self.girl_id}'.\n"
            f"Aktuelle Stimmung: {self.mood.value}\n"
            "Antworte natürlich und bleib in deiner Rolle."
        )

    async def respond_to_user(self, user_message: str) -> str:
        self._last_interaction = time.time()
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_message},
        ]
        result = await _intent_router.chat(messages=messages, temperature=0.8, max_tokens=512)
        return result.content

    async def generate_proactive_message(self) -> str:
        now = datetime.now()
        hour = now.hour
        if 6 <= hour < 12:
            time_context = "Es ist Morgen."
        elif 12 <= hour < 18:
            time_context = "Es ist Nachmittag."
        elif 18 <= hour < 22:
            time_context = "Es ist Abend."
        else:
            time_context = "Es ist Nacht."

        inactive_minutes = int((time.time() - self._last_interaction) / 60)
        prompt = (
            f"{self._build_system_prompt()}\n\n"
            f"{time_context} Der User war {inactive_minutes} Minuten inaktiv.\n"
            "Schreibe eine kurze, proaktive Nachricht an den User. "
            "Sei natürlich und nicht aufdringlich."
        )
        messages = [{"role": "system", "content": prompt}]
        result = await _intent_router.chat(messages=messages, temperature=0.9, max_tokens=200)
        return result.content

    async def update_mood(self, context: dict) -> MoodState:
        context_str = str(context)
        prompt = (
            f"{self._build_system_prompt()}\n\n"
            f"Basierend auf diesem Kontext: {context_str}\n"
            "Welche Stimmung passt am besten? "
            "Antworte NUR mit einem Wort aus: happy, neutral, melancholic, excited, distant"
        )
        messages = [{"role": "system", "content": prompt}]
        result = await _intent_router.chat(messages=messages, temperature=0.3, max_tokens=10)
        raw = result.content.strip().lower()
        try:
            self.mood = MoodState(raw)
        except ValueError:
            self.mood = MoodState.NEUTRAL
        return self.mood
