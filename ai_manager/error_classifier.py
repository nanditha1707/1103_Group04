import anthropic
from google.genai import errors as genai_errors


class ErrorClassifier:
    """Decides what to do after a failed AI request."""

    def __init__(
        self,
        actions: dict[str, str],
        no_text_message: str,
        gemini_timeout_errors: tuple,
        gemini_connection_errors: tuple
    ):
        # Actions returned by classify_error, telling get_ai_response what to
        # do after a failed request.
        self.__actions = actions
        # Error message raised when the AI returns no text. classify_error
        # checks for this exact message to tell it apart from other
        # ValueErrors.
        self.__no_text_message = no_text_message
        # Gemini raises raw httpx / httpx2 errors for timeouts and dropped
        # connections, so both libraries are checked in classify_error.
        self.__gemini_timeout_errors = gemini_timeout_errors
        self.__gemini_connection_errors = gemini_connection_errors