from google import genai
import anthropic
"""
Function to call the gemini API 
Parameters:
prompt(string): The text prompt or instructions you want to send to Gemini model 
api_key: Your personal Google Gemini API key string, required to authenticate and grant permission to access the service.
model: the model or version of Gemini that you want to use
client: Initializes the Google GenAI client object by passing in your api_key. This client handles the network connections and request formatting.
response: Used to Store the full response object received from Google's servers using the command client.models.generate_content(..)
return: Extracts and return just plain generated text through (response.text) back to wherever the function was called.
"""
def call_gemini(
    prompt: str, api_key: str, model: str = "gemini-3.5-flash" 
) -> str: 
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text

def call_claude(
    prompt: str, api_key: str, model: str = "claude-sonnet-5", tokens: int = 1024
    ) -> str:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
        model=model,
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}],
    )
        return response.content[0].text
        
