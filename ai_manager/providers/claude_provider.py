import anthropic

from ai_manager.action import Action
from ai_manager.ai_provider import AIProvider
from ai_manager.empty_reply_error import EmptyReplyError


class ClaudeProvider(AIProvider):
    """Sends requests to the Claude API and classifies its errors."""

    # What to do for each Claude HTTP status code. A code that is not
    # listed is unexpected, so classify_error returns None and the request
    # fails.
    _STATUS_ACTIONS = {
        # Request is too large. Resending the same request will hit the
        # same size limit.
        413: Action.FAIL,
        # Conflict on Anthropic's side. It is transient and usually
        # succeeds on retry.
        409: Action.RETRY_SAME_MODEL,
        # Unexpected internal error on Anthropic's side. It is transient
        # and usually succeeds on retry.
        500: Action.RETRY_SAME_MODEL,
        # Bad gateway, a server between us and Anthropic failed. It is
        # transient and usually succeeds on retry.
        502: Action.RETRY_SAME_MODEL,
        # Service temporarily unavailable. It is transient and usually
        # succeeds on retry.
        503: Action.RETRY_SAME_MODEL,
        # Model not found, e.g. the model ID is wrong or deprecated. That
        # model will never work, but other Claude models may.
        404: Action.SWITCH_MODEL,
        # Request timed out while being processed, the model needed more
        # time than REQUEST_TIMEOUT_SECONDS allows. Retrying with the same
        # timeout will likely time out again, so it is handled the same as
        # a client side timeout.
        504: Action.SWITCH_MODEL,
        # Rate limit reached. Anthropic rate limits are set separately for
        # each model, so another Claude model may still have capacity.
        429: Action.SWITCH_MODEL,
        # API is overloaded, switch to a different model.
        529: Action.SWITCH_MODEL,
        # Invalid request format or content. Every Claude model gets the
        # same request format, so they would all reject it, but other
        # providers build their requests differently and may still work.
        400: Action.SWITCH_PROVIDER,
        # Invalid API key. Every Claude model uses the same key.
        401: Action.SWITCH_PROVIDER,
        # Billing problem, e.g. out of credits. This applies to every
        # Claude model.
        402: Action.SWITCH_PROVIDER,
        # API key lacks permission. This applies to every Claude model.
        403: Action.SWITCH_PROVIDER,
    }

    def call(self, model: str, context: str, prompt: str, schema: dict) -> str:
        """Send a prompt to Claude and return its JSON reply as text.

        'max_retries' is set to 0 because it is better for the retries to
        be handled by the pipeline.
        """
        client = anthropic.Anthropic(
            timeout=self._request_timeout,
            max_retries=0
        )
        response = client.messages.create(
            model=model,
            max_tokens=8000,
            system=context,
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "effort": "high",
                "format": {"type": "json_schema", "schema": schema},
            },
        )
        # If Claude refuses, or the reply is cut off by max_tokens, there is
        # no complete JSON reply. The last content may still be partial text,
        # so stop_reason is checked as well as the content type.
        if (
            response.stop_reason in ("refusal", "max_tokens")
            or not response.content
            or response.content[-1].type != "text"
        ):
            raise EmptyReplyError("Claude returned no text")

        # Slice [-1] to take the last content because Claude outputs its
        # 'thinking and reasoning' steps as well. The last output is the
        # JSON schema containing its response.
        return response.content[-1].text

    def classify_error(self, error: Exception) -> Action | None:
        """Return the Action for an error from the Claude SDK, or None if
        it is not a Claude error."""
        # APITimeoutError is a subclass of APIConnectionError, so it must be
        # checked first. The model needed more time than the request timeout
        # allows, and retrying with the same timeout will likely time out
        # again.
        if isinstance(error, anthropic.APITimeoutError):
            return Action.SWITCH_MODEL

        # The connection dropped, which is likely transient.
        if isinstance(error, anthropic.APIConnectionError):
            return Action.RETRY_SAME_MODEL

        if isinstance(error, anthropic.APIStatusError):
            return self._STATUS_ACTIONS.get(error.status_code)

        return None
