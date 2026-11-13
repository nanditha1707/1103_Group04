from ai_manager.action import Action
from .ai_manager_error import AIManagerError


class MissingApiKeyError(AIManagerError):
    """Raised by a provider when its API key is missing or blank, e.g.
    the .env file has no ANTHROPIC_API_KEY line, or "ANTHROPIC_API_KEY=".

    Every model of that provider uses the same key so its action skips to
    the next provider's models. Without this error the SDKs raise a plain
    TypeError (Claude) or ValueError (Gemini) which neither provider
    recognises, so ErrorClassifier would stop every model.
    """

    action = Action.SWITCH_PROVIDER
