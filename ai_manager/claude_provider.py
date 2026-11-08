import anthropic

from ai_provider import AiProvider


class ClaudeProvider(AiProvider):
    """Sends requests to the Claude API."""

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
        # so stop_reason is checked as well as the content type. Raise
        # ValueError with NO_TEXT_ERROR_MESSAGE so the error is classified
        # as SWITCH_MODEL. The same prompt sent to the same model is likely
        # to fail the same way, so retrying would waste time.
        if (
            response.stop_reason in ("refusal", "max_tokens")
            or not response.content
            or response.content[-1].type != "text"
        ):
            raise ValueError(self._no_text_message)

        # Slice [-1] to take the last content because Claude outputs its
        # 'thinking and reasoning' steps as well. The last output is the
        # JSON schema containing its response.
        return response.content[-1].text
