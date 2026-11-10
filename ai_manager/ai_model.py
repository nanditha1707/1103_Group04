from dataclasses import dataclass

from .ai_provider import AIProvider


@dataclass(frozen=True)
class AIModel:
    provider: AIProvider
    name: str
