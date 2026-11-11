from dataclasses import dataclass

from .ai_provider import AIProvider


@dataclass(frozen=True)
class AIModel:
    """One model to try: the provider that serves it and the model's
    name, e.g. a ClaudeProvider and "claude-opus-5-5".

    Models from the same provider share one provider object. That is how
    ModelFallback finds the next model from a different provider.
    """

    provider: AIProvider
    name: str
