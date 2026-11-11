from dataclasses import dataclass
from .ai_provider import AIProvider


@dataclass(frozen=True)
class AIModel:
    """One model to be used to generate the AI response.

    Models from the same provider share one provider object. That is how
    ModelFallback finds the next model from a different provider.
    """

    provider: AIProvider
    name: str
