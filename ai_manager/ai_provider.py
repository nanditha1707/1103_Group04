from abc import ABC, abstractmethod


class AiProvider(ABC):
    """Base class for an AI provider (Claude, Gemini). Each provider
    sends one request to one model and returns the JSON reply as text."""

    def __init__(self, request_timeout: int, no_text_message: str):
        # Timeout for 1 AI API request.
        self._request_timeout = request_timeout
        # Error message raised when the AI returns no text. classify_error
        # checks for this exact message to tell it apart from other
        # ValueErrors.
        self._no_text_message = no_text_message

    @abstractmethod
    def call(self, model: str, context: str, prompt: str, schema: dict) -> str:
        """Send a prompt to the model and return its JSON reply as text."""