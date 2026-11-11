class MissingApiKeyError(Exception):
    """Raised by a provider when its API key is missing or blank, e.g.
    the .env file has no ANTHROPIC_API_KEY line, or "ANTHROPIC_API_KEY=".

    Every model of that provider uses the same key so ErrorClassifier
    skips to the next provider's models. Without this error the SDKs raise
    a plain TypeError (Claude) or ValueError (Gemini) which neither
    provider recognises, so ErrorClassifier would stop every model.
    """
