import os
from abc import ABC, abstractmethod

from .action import Action
from .ai_request import AIRequest
from .missing_api_key_error import MissingApiKeyError


class AIProvider(ABC):
    """Interface for an AI provider such as Claude or Gemini.

    A provider does 2 things for its own API:
    1. send() sends one request to one of its models and returns the
       JSON reply as text.
    2. classify_error() decides what to do when send() fails, because
       only the provider knows its own SDK's errors and status codes.

    ModelFallback and ErrorClassifier only call these 2 methods, so a new
    provider is a new subclass plus its models in AIManager, with no
    change to the retry logic.
    """

    @abstractmethod
    def send(self, model: str, request: AIRequest) -> str:
        """Send the request to the model and return its JSON reply as text.

        Raises EmptyReplyError if the model returns no usable text, and
        MissingApiKeyError if the provider's API key is missing or blank.
        Any other error comes from the provider's SDK and is passed to
        classify_error().
        """

    @abstractmethod
    def classify_error(self, error: Exception) -> Action | None:
        """Return the Action for an error raised by send(), or None if this
        provider does not recognise the error."""

    @staticmethod
    def _read_api_key(variable: str) -> str:
        """Return the API key held in the environment variable, for a
        subclass to pass to its SDK client.

        Raises MissingApiKeyError if it is missing or blank, e.g. the .env
        file has "GEMINI_API_KEY=" with nothing after it.
        """
        api_key = os.environ.get(variable)

        if not api_key:
            raise MissingApiKeyError(f"{variable} is missing or blank")

        return api_key
