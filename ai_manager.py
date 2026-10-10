# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import json
import time

import anthropic
import httpx
import httpx2
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

FAIL = "Fail immediately"
RETRY_SAME_MODEL = "Retry on the same model"
SWITCH_MODEL = "Switch models"
SWITCH_MODEL_PROVIDER = "Switch immediately to a different model provider"
GEMINI_TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
GEMINI_CONNECTION_ERRORS = (httpx.ConnectError, httpx2.ConnectError)
REQUEST_TIMEOUT_SECONDS = 20
TOTAL_TIMEOUT_SECONDS = 60
MAX_RETRIES_PER_MODEL = 2
CONTACT_SUPPORT_MESSAGE = "Something went wrong. Please try again later or contact support."

MODELS = [
    {"provider": "claude", "model": "claude-opus-5-5"},
    {"provider": "claude", "model": "claude-sonnet-5"},
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
    {"provider": "gemini", "model": "gemini-3.1-flash-lite"},
]

# Reads API key from local .env file.
load_dotenv()

# ======================================================================
# CALL FUNCTIONS FOR CLAUDE AND GEMINI
# ======================================================================

def call_gemini(model, context, prompt, schema) -> str:
    """Send a prompt to Gemini and return its JSON reply as text.

    Gemini's timeout is in milliseconds, so timeout multiplied by 1000.

    'attempts' is set to 1 (the original request only, no retries)
    because it is better for the retries to be handled by the pipeline.
    """
    client = genai.Client(
        http_options={
            "timeout": REQUEST_TIMEOUT_SECONDS * 1000,
            "retry_options": {"attempts": 1},
        })
    response = client.models.generate_content(
        model=model, contents=prompt, config={
            "system_instruction": context,
            "response_mime_type": "application/json",
            "response_json_schema": schema,
        },
    )
    return response.text


def call_claude(model, context, prompt, schema) -> str:
    """Send a prompt to Claude and return its JSON reply as text.

    'max_retries' is set to 0 because it is better for the retries to
    be handled by the pipeline.
    """
    client = anthropic.Anthropic(timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0)
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
    return response.content[-1].text

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

def next_provider_index(current_model_index, selected_model_provider):

    for next_model_index in range(current_model_index + 1, len(MODELS)):
        if MODELS[next_model_index]["provider"] != selected_model_provider:
            # return the index of the next model
            return next_model_index
        
    # return len of models so the while loop in get_ai_response stops when 
    # theres no other model to switch to
    return len(MODELS)

def parse_ai_response(text):
    return json.loads(text)

# ======================================================================
# CORE FUNCTIONS
# ======================================================================
def get_ai_response(context, prompt, schema):
    """Try each model in MODELS until one returns a valid reply, and
    return it as a dict. Errors are handled using classify_error. If
    every model fails or the total time runs out, return an error dict.
    """
    deadline = time.time() + TOTAL_TIMEOUT_SECONDS
    model_index = 0
    retries = 0

    while model_index < len(MODELS) and time.time() < deadline:
        provider = MODELS[model_index]["provider"]
        model = MODELS[model_index]["model"]

        try:
            if provider == "claude":
                ai_response = call_claude(model, context, prompt, schema)
            else:
                ai_response = call_gemini(model, context, prompt, schema)
            return parse_ai_response(ai_response)

        except Exception as error:
            action = classify_error(error)
            print(f"{provider} | {model}: {error} -> {action}")

            if action == FAIL:
                break

            # Wait longer after each retry. 'continue' skips the reset of
            # retries below, since it should only reset on a model change.
            if action == RETRY_SAME_MODEL and retries < MAX_RETRIES_PER_MODEL:
                retries += 1
                time.sleep(retries)
                continue

            if action == SWITCH_MODEL_PROVIDER:
                model_index = next_provider_index(model_index, provider)
            else:
                # SWITCH_MODEL, or RETRY_SAME_MODEL with no retries left
                model_index += 1
            retries = 0

    return {"error": CONTACT_SUPPORT_MESSAGE}
