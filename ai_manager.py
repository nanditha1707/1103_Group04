"""Functions for calling the Gemini and Claude APIs."""
import json

import anthropic
import httpx
from google import genai
from google.genai import types, errors


def call_gemini(prompt, api_key, model="gemini-3.5-flash", tokens=1024):
    """
    Function to call the gemini API.

    Parameters:
        prompt (string): The text prompt or instructions you want to send to Gemini model.
        api_key: Your personal Google Gemini API key string, required to authenticate
            and grant permission to access the service.
        model: The model or version of Gemini that you want to use.
        tokens: The maximum number of tokens the model is allowed to use to generate
            its response.

    Variables:
        client: Initializes the Google GenAI client object by passing in your api_key.
            This client handles the network connections and request formatting.
        response: Used to store the full response object received from Google's servers
            using the command client.models.generate_content(..).

    Returns:
        Extracts and returns just the plain generated text (response.text) back to
        wherever the function was called.
    """
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=10_000,  # 10s rule done (milliseconds in Gemini)
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(  # this is necessary for gemini due to different sdk
            max_output_tokens=tokens,  # added max tokens
        ),
    )
    return response.text or ""


def call_claude(
    prompt: str, api_key: str, model: str = "claude-sonnet-5", tokens: int = 1024
) -> str:
    """
    Function to call the claude API.

    Parameters Added On:
        tokens: This parameter specifies the maximum number of tokens that the model
            is allowed to use to generate its response.
    """
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def gemini_classify_error(error):  # pylint: disable=too-many-return-statements
    """Returns 1, 2 or 3:
    1 = give up 400,401,403,429,499
    2 = retry the same model 500
    3 = switch to a different Gemini model 404
    """
    # very slow then it will retry
    if isinstance(error, (httpx.TimeoutException, httpx.TransportError)):
        return 2

    # json crash handling (just in case model outputs bad JSON string)
    if isinstance(error, json.JSONDecodeError):
        return 2

    # client side error (4xx)
    if isinstance(error, errors.ClientError):
        code = getattr(error, "code", None)
        if code in (400, 401, 403, 429, 499):
            return 1  # Give up
        if code == 404:
            return 3  # 3 -> 1
        return 1  # Default fallback for other 4xx errors

    # server side error (5xx)
    if isinstance(error, errors.ServerError):
        code = getattr(error, "code", None)
        if code == 500:
            return 2  # 2
        if code == 503:
            return 2  # 2 -> 1
        if code == 504:
            return 2  # 2 -> 1
        return 1  # Default fallback for other 5xx server errors

    print("Unknown error code")  # Error code printed out if none of the above conditions are met
    return None