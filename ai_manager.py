from google import genai

def call_gemini(
    prompt: str, api_key: str, model: str = "gemini-3.5-flash"
) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
