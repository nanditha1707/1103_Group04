import anthropic

from ai_provider import AiProvider


class ClaudeProvider(AiProvider):
    """Sends requests to the Claude API."""