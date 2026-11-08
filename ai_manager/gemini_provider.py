from google import genai

from ai_provider import AiProvider


class GeminiProvider(AiProvider):
    """Sends requests to the Gemini API."""