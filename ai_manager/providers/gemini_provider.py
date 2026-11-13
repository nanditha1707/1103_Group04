import httpx
import httpx2
from google import genai
from google.genai import errors as genai_errors

from ai_manager.action import Action
from ai_manager.ai_provider import AIProvider
from ai_manager.ai_request import AIRequest
from ai_manager.errors import EmptyReplyError


class GeminiProvider(AIProvider):
    """Sends requests to the Gemini API and classifies its errors."""

    # Environment variable, set from the .env file, that holds the key.
    _API_KEY_VARIABLE = "GEMINI_API_KEY"

    # Gemini raises raw httpx / httpx2 errors for timeout and connection
    # errors.
    _TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
    _CONNECTION_ERRORS = (httpx.TransportError, httpx2.TransportError)

    # IMPORTANT: Different model providers have different error codes
    # so this has to be defined in each model provider instead of being shared
    # What to do for each Gemini HTTP status code. A code that is not
    # listed is unexpected, so classify_error returns None and the request
    # fails.
    _STATUS_ACTIONS = {
        # Request is too large. Resending the same request will hit the
        # same size limit.
        413: Action.FAIL,

        # Unexpected internal error on Google's side. It is transient and
        # usually succeeds on retry.
        500: Action.RETRY_SAME_MODEL,

        # Bad gateway, a server between us and Google failed. It is
        # transient and usually succeeds on retry.
        502: Action.RETRY_SAME_MODEL,

        # Model not found, e.g. the model ID is wrong or deprecated. That
        # model will never work, but other Gemini models may.
        404: Action.SWITCH_MODEL,

        # Deadline exceeded, the model needed more time than
        # REQUEST_TIMEOUT_SECONDS allows. Retrying with the same timeout
        # will likely time out again, so it is handled the same as a client
        # side timeout.
        504: Action.SWITCH_MODEL,

        # Quota or rate limit exhausted. Gemini quotas are per model, so
        # another Gemini model may still have quota left.
        429: Action.SWITCH_MODEL,

        # Service unavailable or overloaded. Another model may not be
        # overloaded.
        503: Action.SWITCH_MODEL,

        # Invalid argument or malformed request. Every Gemini model gets the
        # same request, so they would all reject it, but other providers
        # build their requests differently and may still work.
        400: Action.SWITCH_PROVIDER,

        # Invalid API key. Every Gemini model uses the same key.
        401: Action.SWITCH_PROVIDER,

        # API key lacks permission. This applies to every Gemini model.
        403: Action.SWITCH_PROVIDER,
    }

    def __init__(
        self, request_timeout: int, client: genai.Client | None = None
    ):
        # Timeout for 1 AI API request, in seconds.
        self.__request_timeout = request_timeout
        # A client can be passed in, e.g. a fake one in tests. Otherwise it
        # is created on the first request. See __get_client below.
        self.__client = client

    def send(self, model: str, request: AIRequest) -> str:
        """Send the request to Gemini and return its JSON reply as text."""
        response = self.__get_client().models.generate_content(
            model=model,
            contents=request.prompt,
            config={
                "system_instruction": request.context,
                "response_mime_type": "application/json",
                "response_json_schema": request.schema,
            },
        )
        # response.text is None when Gemini returns no text, such as when a
        # safety filter blocks the reply.
        if not response.text:
            raise EmptyReplyError("Gemini returned no text")

        return response.text

    def classify_error(self, error: Exception) -> Action | None:
        """Return the Action for an error from the Gemini SDK, or None if
        it is not a Gemini error."""
        # The model needed more time than the request timeout allows, and
        # retrying with the same timeout will likely time out again.
        if isinstance(error, self._TIMEOUT_ERRORS):
            return Action.SWITCH_MODEL

        # The connection dropped, which is likely transient.
        if isinstance(error, self._CONNECTION_ERRORS):
            return Action.RETRY_SAME_MODEL

        if isinstance(error, genai_errors.APIError):
            return self._STATUS_ACTIONS.get(error.code)

        return None

    def __get_client(self) -> genai.Client:
        """Return the Gemini client, creating it on the first request.

        It is created here and not in __init__ so the program still starts
        without a key, and any error is raised by send() and classified
        like every other error.

        Raises MissingApiKeyError if GEMINI_API_KEY is missing or blank, so
        ModelFallback moves on to the next provider. Otherwise genai.Client
        raises a ValueError, which classify_error does not recognise, so
        every model would stop.
        The key is passed to the client, so the key that was checked is the
        one used, even if GOOGLE_API_KEY is also set.

        Gemini's timeout is in milliseconds, so it is multiplied by 1000.
        'attempts' is set to 1 (the original request only, no retries)
        because ModelFallback handles retries.
        """
        if self.__client is None:
            self.__client = genai.Client(
                api_key=self._read_api_key(self._API_KEY_VARIABLE),
                http_options={
                    "timeout": self.__request_timeout * 1000,
                    "retry_options": {"attempts": 1},
                }
            )
        return self.__client
