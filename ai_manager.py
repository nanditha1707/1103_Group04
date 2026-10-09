# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================

import anthropic
import httpx
import httpx2
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

FAIL = "Fail immediately"
RETRY_SAME_MODEL = "Retry on the same model"
SWITCH_MODEL = "Switch models"
SWITCH_MODEL_PROVIDER = "Switch immediately to a different model provider"
GEMINI_TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
GEMINI_CONNECTION_ERRORS = (httpx.ConnectError, httpx2.ConnectError)

# Reads API key from local .env file.
load_dotenv()

# ======================================================================
# CALL FUNCTIONS FOR CLAUDE AND GEMINI
# ======================================================================

def call_gemini(prompt, api_key, model="gemini-3.5-flash", tokens=1024):
    """
    Function to call the gemini API.

    Parameters:
        prompt: The text prompt or instructions you want to send to Gemini model.
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

# ======================================================================
# ERROR CLASSIFICATION FUNCTIONS FOR CLAUDE AND GEMINI
# ======================================================================
def classify_error(error):
    """Unified function to classify all API errors from Claude and
    Gemini. It classifies the error based on either the error code or
    for errors without error codes, the error itself, and returns a
    suitable action to take based on the error message."""

    # Something wrong with json generation
    if isinstance(error, ValueError):
        return RETRY_SAME_MODEL
    
    # Claude errors
    # APITimeoutError is a subclass of APIConnectionError
    # So it has to be checked BEFORE APIConnectionError
    if isinstance(error, anthropic.APITimeoutError):
        return SWITCH_MODEL
    if isinstance(error, anthropic.APIConnectionError):
        return RETRY_SAME_MODEL
    if isinstance(error, anthropic.APIStatusError):
        error_code = error.status_code
        if error_code in (400, 413):
            return FAIL
        elif error_code in (401, 402, 403, 429):
            return SWITCH_MODEL_PROVIDER
        elif error_code in (404, 529):
            return SWITCH_MODEL
        elif error_code in (409, 500, 504):
            return RETRY_SAME_MODEL

    # Gemini Errors
    if isinstance(error, GEMINI_TIMEOUT_ERRORS):
        return SWITCH_MODEL
    
    if isinstance(error, GEMINI_CONNECTION_ERRORS):
        return RETRY_SAME_MODEL
    
    if isinstance(error, genai_errors.APIError):
        error_code = error.code
        if error_code in (500, 504):
            return RETRY_SAME_MODEL
        elif error_code in (400, 413):
            return FAIL
        elif error_code in (401, 403):
            return SWITCH_MODEL_PROVIDER
        elif error_code in (404, 429, 503):
            return SWITCH_MODEL

    # Unexpected errors that dont classify
    return FAIL