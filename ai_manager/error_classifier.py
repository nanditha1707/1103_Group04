import anthropic
from google.genai import errors as genai_errors

from .action import Action
from .empty_reply_error import EmptyReplyError


class ErrorClassifier:
    """Decides what to do after a failed AI request."""

    def __init__(
        self, gemini_timeout_errors: tuple, gemini_connection_errors: tuple
    ):
        # Gemini raises raw httpx / httpx2 errors for timeouts and dropped
        # connections, so both libraries are checked in classify_error.
        self.__gemini_timeout_errors = gemini_timeout_errors
        self.__gemini_connection_errors = gemini_connection_errors

    def classify(self, error: Exception) -> Action:
        """Unified function to classify all API errors from Claude and
        Gemini. It classifies the error based on either the error code or
        for errors without error codes, the error itself, and returns the
        Action to take.

        Claude error codes:
            413 (FAIL): Request is too large. Resending the same request
                will hit the same size limit.
            409 (RETRY_SAME_MODEL): Conflict on Anthropic's side. It is
                transient and usually succeeds on retry.
            500 (RETRY_SAME_MODEL): Unexpected internal error on
                Anthropic's side. It is transient and usually succeeds
                on retry.
            502 (RETRY_SAME_MODEL): Bad gateway, a server between us and
                Anthropic failed. It is transient and usually succeeds
                on retry.
            503 (RETRY_SAME_MODEL): Service temporarily unavailable. It
                is transient and usually succeeds on retry.
            404 (SWITCH_MODEL): Model not found, e.g. the model ID is
                wrong or deprecated. That model will never work, but
                other Claude models may.
            504 (SWITCH_MODEL): Request timed out while being processed,
                the model needed more time than REQUEST_TIMEOUT_SECONDS
                allows. Retrying with the same timeout will likely time out
                again, so it is handled the same as a client side timeout.
            429 (SWITCH_MODEL): Rate limit reached. Anthropic rate limits
                are set separately for each model, so another Claude model
                may still have capacity.
            529 (SWITCH_MODEL): API is overloaded, switch to a different
                model API.
            400 (SWITCH_PROVIDER): Invalid request format or
                content. Every Claude model gets the same request format, 
                so they would all reject it, but other models request format
                is built differently and may still work.
            401 (SWITCH_PROVIDER): Invalid API key. Every Claude
                model uses the same key, so switch models.
            402 (SWITCH_PROVIDER): Billing problem, e.g. out of
                credits. This applies to every Claude model.
            403 (SWITCH_PROVIDER): API key lacks permission. This
                applies to every Claude model.

        Gemini error codes:
            413 (FAIL): Request is too large. Resending the same request
                will hit the same size limit.
            500 (RETRY_SAME_MODEL): Unexpected internal error on Google's
                side. It is transient and usually succeeds on retry.
            502 (RETRY_SAME_MODEL): Bad gateway, a server between us and
                Google failed. It is transient and usually succeeds on
                retry.
            404 (SWITCH_MODEL): Model not found, e.g. the model ID is
                wrong or deprecated. That model will never work, but
                other Gemini models may.
            504 (SWITCH_MODEL): Deadline exceeded, the model needed more
                time than REQUEST_TIMEOUT_SECONDS allows. Retrying with
                the same timeout will likely time out again, so it is
                handled the same as a client side timeout.
            429 (SWITCH_MODEL): Quota or rate limit exhausted. Gemini
                quotas are per model, so another Gemini model may still
                have quota left.
            503 (SWITCH_MODEL): Service unavailable or overloaded.
                Another model may not be overloaded.
            400 (SWITCH_PROVIDER): Invalid argument or malformed
                request. Every Gemini model gets the same request, so
                they would all reject it, but other model requests are built
                differently and may still work.
            401 (SWITCH_PROVIDER): Invalid API key. Every Gemini
                model uses the same key, so switch models.
            403 (SWITCH_PROVIDER): API key lacks permission. This
                applies to every Gemini model.
        """

        # The model answered with no text, e.g. it refused or a safety
        # filter blocked it. The same prompt sent to the same model is
        # likely to fail the same way, so retrying would waste time.
        if isinstance(error, EmptyReplyError):
            return Action.SWITCH_MODEL

        # If something is wrong with json output or the AI output failed
        # validation then retry same model because the error is likely
        # transient.
        if isinstance(error, ValueError):
            return Action.RETRY_SAME_MODEL

        # Claude errors
        if isinstance(error, anthropic.APITimeoutError):
            return Action.SWITCH_MODEL

        elif isinstance(error, anthropic.APIConnectionError):
            return Action.RETRY_SAME_MODEL

        elif isinstance(error, anthropic.APIStatusError):
            error_code = error.status_code
            if error_code == 413:
                return Action.FAIL
            elif error_code in (409, 500, 502, 503):
                return Action.RETRY_SAME_MODEL
            elif error_code in (404, 429, 504, 529):
                return Action.SWITCH_MODEL
            elif error_code in (400, 401, 402, 403):
                return Action.SWITCH_PROVIDER

        # Gemini Errors
        if isinstance(error, self.__gemini_timeout_errors):
            return Action.SWITCH_MODEL

        elif isinstance(error, self.__gemini_connection_errors):
            return Action.RETRY_SAME_MODEL

        elif isinstance(error, genai_errors.APIError):
            error_code = error.code
            if error_code == 413:
                return Action.FAIL
            elif error_code in (500, 502):
                return Action.RETRY_SAME_MODEL
            elif error_code in (404, 429, 503, 504):
                return Action.SWITCH_MODEL
            elif error_code in (400, 401, 403):
                return Action.SWITCH_PROVIDER

        # Unexpected errors that dont classify.
        return Action.FAIL