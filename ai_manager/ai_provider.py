from abc import ABC, abstractmethod


class AiProvider(ABC):
    """Base class for an AI provider (Claude, Gemini). Each provider
    sends one request to one model and returns the JSON reply as text."""

    def __init__(self, request_timeout: int):
        # Timeout for 1 AI API request.
        self._request_timeout = request_timeout

    @abstractmethod
    def call(self, model: str, context: str, prompt: str, schema: dict) -> str:
        """Send a prompt to the model and return its JSON reply as text.

        Raises EmptyReplyError if the model returns no usable text.
        """