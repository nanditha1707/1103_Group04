"""AI manager: sends prompts to Claude or Gemini with retries and fallbacks."""

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
    """Return the index of the next model from a different provider."""

    for next_model_index in range(current_model_index + 1, len(MODELS)):
        if MODELS[next_model_index]["provider"] != selected_model_provider:
            # return the index of the next model
            return next_model_index

    # return len of models so the while loop in get_ai_response stops when
    # theres no other model to switch to
    return len(MODELS)

def parse_ai_response(text):
    """Parse the AI's JSON text output into a Python dictionary."""
    return json.loads(text)

# ======================================================================
# CORE FUNCTIONS
# ======================================================================
def get_ai_response(context, prompt, schema):
    """Try each model in MODELS until one returns a valid JSON reply.

    Errors are classified to decide whether to retry, switch model,
    switch provider or fail. Returns an error dict if nothing works
    before the total deadline.
    """
    deadline = time.time() + TOTAL_TIMEOUT_SECONDS
    current_model_index = 0
    current_retries = 0

    while current_model_index < len(MODELS) and time.time() < deadline:
        selected_model = MODELS[current_model_index]
        selected_model_provider = selected_model["provider"]
        selected_model_name = selected_model["model"]
        try:
            if selected_model_provider == "claude":
                ai_response = call_claude(selected_model_name, context, prompt, schema)
            elif selected_model_provider == "gemini":
                ai_response = call_gemini(selected_model_name, context, prompt, schema)

            # unrecognised model name -> go to next model in MODELS
            else:
                print(f"{selected_model_provider} | {selected_model_name} "
                      f"unknown provider '{selected_model_provider}' -> skipping")
                current_model_index += 1
                continue

            # if no problems then return parse ai output and return it
            return parse_ai_response(ai_response)

        except Exception as error: 
            # take an action based on the returned error
            action = classify_error(error)
            print(f"{selected_model_provider} {selected_model_name} {error} -> {action}")

            # if fail then break entire loop
            if action == FAIL:
                break
            if action == RETRY_SAME_MODEL and current_retries < MAX_RETRIES_PER_MODEL:
                current_retries += 1

                # Typical retry logic is that time between retries
                # should increase as number of retries increase.
                # .sleep increases delay time between
                # successive retries.
                time.sleep(current_retries)

                # This continue skips current_retries = 0 as we only
                # want retries to be reset upon changing models
                # or model providers.
                continue
            if action == SWITCH_MODEL_PROVIDER:
                current_model_index = next_provider_index(
                    current_model_index, selected_model_provider)

            elif action in (SWITCH_MODEL, RETRY_SAME_MODEL):
                # RETRY_SAME_MODEL only reaches here once retries are used up
                current_model_index += 1

            else:
                # unhandled action: fail rather than guess
                print("An unexpected error has occured")
                break

            # Reset retry count. It should only be reached when
            # action is SWITCH_MODEL or SWITCH_MODEL_PROVIDER.
            current_retries = 0

    return {"error": CONTACT_SUPPORT_MESSAGE}

def create_ai_prompt(ai_answers: dict) -> str:
    """Build the patient intake prompt from the already filtered answers
    """
    ai_prompt = "Presenting patient answers:\n"

    for key, value in ai_answers.items():
        ai_prompt += f"- {key}: {value}\n"

    return ai_prompt