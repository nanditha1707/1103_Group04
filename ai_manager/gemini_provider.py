from google import genai

from .ai_provider import AiProvider
from .empty_reply_error import EmptyReplyError


class GeminiProvider(AiProvider):
    """Sends requests to the Gemini API."""

    def call(self, model: str, context: str, prompt: str, schema: dict) -> str:
        """Send a prompt to Gemini and return its JSON reply as text.

        Gemini's timeout is in milliseconds, so timeout multiplied by 1000.

        'attempts' is set to 1 (the original request only, no retries)
        because it is better for the retries to be handled by the pipeline.
        """
        client = genai.Client(
            http_options={
                "timeout": self._request_timeout * 1000,
                "retry_options": {"attempts": 1},
            })
        response = client.models.generate_content(
            model=model, contents=prompt, config={
                "system_instruction": context,
                "response_mime_type": "application/json",
                "response_json_schema": schema,
            },
        )
        # response.text is None when Gemini returns no text, such as when a
        # safety filter blocks the reply.
        if not response.text:
            raise EmptyReplyError("Gemini returned no text")

        return response.text