from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class CharacterSheet:
    name: str
    age: int
    personality: str
    appearance: str
    voice_model: str
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if self.age < 18:
            raise ValueError(
                f"Character age must be >= 18 (got {self.age}). "
                "All characters on this platform must be adults."
            )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "personality": self.personality,
            "appearance": self.appearance,
            "voice_model": self.voice_model,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterSheet":
        return cls(
            name=data["name"],
            age=data["age"],
            personality=data.get("personality", ""),
            appearance=data.get("appearance", ""),
            voice_model=data.get("voice_model", ""),
            created_at=data.get("created_at", time.time()),
        )
