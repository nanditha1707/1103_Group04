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

    def classify(self, error: Exception) -> str:
        """Unified function to classify all API errors from Claude and
        Gemini. It classifies the error based on either the error code or
        for errors without error codes, the error itself, and returns a
        suitable ACTION (a constant) to take based on the error message.

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
            400 (SWITCH_MODEL_PROVIDER): Invalid request format or
                content. Every Claude model gets the same request format, 
                so they would all reject it, but other models request format
                is built differently and may still work.
            401 (SWITCH_MODEL_PROVIDER): Invalid API key. Every Claude
                model uses the same key, so switch models.
            402 (SWITCH_MODEL_PROVIDER): Billing problem, e.g. out of
                credits. This applies to every Claude model.
            403 (SWITCH_MODEL_PROVIDER): API key lacks permission. This
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
            400 (SWITCH_MODEL_PROVIDER): Invalid argument or malformed
                request. Every Gemini model gets the same request, so
                they would all reject it, but other model requests are built
                differently and may still work.
            401 (SWITCH_MODEL_PROVIDER): Invalid API key. Every Gemini
                model uses the same key, so switch models.
            403 (SWITCH_MODEL_PROVIDER): API key lacks permission. This
                applies to every Gemini model.
        """

        fail = self.__actions["fail"]
        retry_same_model = self.__actions["retry_same_model"]
        switch_model = self.__actions["switch_model"]
        switch_model_provider = self.__actions["switch_model_provider"]

        # If the AI returned no text then switch model because the same
        # model is likely to fail the same way again. This must be checked
        # before the general ValueError check below.
        if isinstance(error, ValueError) and str(error) == self.__no_text_message:
            return switch_model

        # If something is wrong with json output or the AI output failed
        # validation then retry same model because the error is likely
        # transient.
        if isinstance(error, ValueError):
            return retry_same_model

        # Claude errors
        if isinstance(error, anthropic.APITimeoutError):
            return switch_model

        elif isinstance(error, anthropic.APIConnectionError):
            return retry_same_model

        elif isinstance(error, anthropic.APIStatusError):
            error_code = error.status_code
            if error_code == 413:
                return fail
            elif error_code in (409, 500, 502, 503):
                return retry_same_model
            elif error_code in (404, 429, 504, 529):
                return switch_model
            elif error_code in (400, 401, 402, 403):
                return switch_model_provider

        # Gemini Errors
        if isinstance(error, self.__gemini_timeout_errors):
            return switch_model

        elif isinstance(error, self.__gemini_connection_errors):
            return retry_same_model

        elif isinstance(error, genai_errors.APIError):
            error_code = error.code
            if error_code == 413:
                return fail
            elif error_code in (500, 502):
                return retry_same_model
            elif error_code in (404, 429, 503, 504):
                return switch_model
            elif error_code in (400, 401, 403):
                return switch_model_provider

        # Unexpected errors that dont classify.
        return fail