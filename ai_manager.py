# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import json
import time

import anthropic
import httpx
import httpx2
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

# Timeout for 1 AI API request.
REQUEST_TIMEOUT_SECONDS = 20
# Timeout for all API requests to return a valid answer. 
TOTAL_TIMEOUT_SECONDS = 60
# Retry number for retrying on same the same model.
MAX_RETRIES_PER_MODEL = 2
# Models to use for the AI API, in order of execution.
MODELS = [
    {"provider": "claude", "model": "claude-opus-5-5"},
    {"provider": "claude", "model": "claude-sonnet-5"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
]

FILE_PATH_ICD11 = "datasets/icd11.csv"
FILE_PATH_HSA = "datasets/hsa.csv"

FAIL = "Fail immediately"
RETRY_SAME_MODEL = "Retry on the same model"
SWITCH_MODEL = "Switch models"
SWITCH_MODEL_PROVIDER = "Switch immediately to a different model provider"
CONTACT_SUPPORT_MESSAGE = (
    "Please contact technical staff for assistance. "
    "Either an unexpected error has occured or all AI APIs are currently down. "
)

GEMINI_TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
GEMINI_CONNECTION_ERRORS = (httpx.ConnectError, httpx2.ConnectError)

AI_OUTPUT_FIELDS = {
    "primary_diagnosis_ICD11_Title": {"type": "string"},
    "primary_diagnosis_ICD11_Code": {"type": "string"},
    "primary_diagnosis_explanation": {"type": "string"},
    "secondary_diagnosis_ICD11_Title": {"type": "string"},
    "secondary_diagnosis_ICD11_Code": {"type": "string"},
    "secondary_diagnosis_explanation": {"type": "string"},
    "primary_diagnosis_medicine_1":{"type": "string"},
    "primary_diagnosis_medicine_2":{"type": "string"},
    "secondary_diagnosis_medicine_1":{"type": "string"},
    "secondary_diagnosis_medicine_2":{"type": "string"},
    "ai_confidence_score":{"type": "integer"},
}

AI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": AI_OUTPUT_FIELDS,
    "required": list(AI_OUTPUT_FIELDS.keys()),
    "additionalProperties": False,
}

AI_MEDICAL_CONTEXT = """
You are a clinical decision support assistant at a primary care clinic in Singapore.
Your goal is to effectively and accurately triage patients based on the patient
details provided to you. Your output is reviewed by a certified medical professional
and is not a final diagnosis.

Task:
- Based on the patient's intake answers, suggest 2 diagnosis: 1 likely primary and 
  1 likely secondary diagnosis using ICD-11 titles and their respective codes.
- Suggest up to two suitable medicines for each diagnosis.

Explanations:
- Briefly explain the reasoning behind each diagnosis in
  primary_diagnosis_explanation and secondary_diagnosis_explanation.
- Put explanations only in those two fields and nowhere else.
- Keep each explanation to 120 characters or fewer.
- Explanations are shown mainly to patients but also to doctors, so avoid complex
  medical terms.

Confidence and refusal:
- ai_confidence_score is an integer from 0 to 100 showing how confident you are in
  the primary diagnosis.
- If you cannot give a valid answer to the prompt, set ai_confidence_score to 0, 
  and make all other fields empty strings.

Emergency:
- If you believe the patients requires urgent and immediate care, include the word
"EMERGENCY" in at least one of your explanation fields and set the medicine fields to ' '.
- Still provide 2 likely diagnoses using ICD-11 titles and its respective codes.

Symptom definitions:
- 'high fever' means a temperature at or above 39 degrees Celsius.
- 'fever' means a temperature below 39 degrees Celsius."""

DF_ICD11 = pd.read_csv(FILE_PATH_ICD11)
DF_HSA = pd.read_csv(FILE_PATH_HSA)
VALID_DIAGNOSES = DF_ICD11["Title"].str.strip().str.upper()
VALID_CODES = DF_ICD11["Code"].str.strip().str.upper()
VALID_MEDICINES = pd.concat(
    [DF_HSA["Productname"], DF_HSA["Activeingredients"]]
).str.strip().str.upper()

# Reads API key from local .env file.
load_dotenv()


# ======================================================================
# API CALL FUNCTIONS
# ======================================================================
def call_gemini(model: str, context: str, prompt: str, schema: dict) -> str:
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


def call_claude(model: str, context: str, prompt: str, schema: dict) -> str:
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
    # Slice [-1] to take the last content because Claude outputs its
    # 'thinking and reasoning' steps as well. The last output is the
    # JSON schema containing its response. 
    return response.content[-1].text


# ======================================================================
# ERROR CLASSIFICATION FUNCTIONS
# ======================================================================
def classify_error(error: Exception) -> str:
    """Unified function to classify all API errors from Claude and
    Gemini. It classifies the error based on either the error code or
    for errors without error codes, the error itself, and returns a
    suitable action to take based on the error message."""

    # If something is wrong with json output, or AI output failed 
    # validation then retry same model because error is likely transient.
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
        elif error_code in (409, 500, 504):
            return RETRY_SAME_MODEL
        elif error_code in (404, 529):
            return SWITCH_MODEL
        elif error_code in (401, 402, 403, 429):
            return SWITCH_MODEL_PROVIDER

    # Gemini Errors
    if isinstance(error, GEMINI_TIMEOUT_ERRORS):
        return SWITCH_MODEL

    if isinstance(error, GEMINI_CONNECTION_ERRORS):
        return RETRY_SAME_MODEL

    if isinstance(error, genai_errors.APIError):
        error_code = error.code
        if error_code in (400, 413):
            return FAIL
        elif error_code in (500, 504):
            return RETRY_SAME_MODEL
        elif error_code in (404, 429, 503):
            return SWITCH_MODEL
        elif error_code in (401, 403):
            return SWITCH_MODEL_PROVIDER

    # Unexpected errors that dont classify. In
    return FAIL


def next_provider_index(current_model_index: int, selected_model_provider: str) -> int:
    """Return the index of the next model from a different provider."""

    for next_model_index in range(current_model_index + 1, len(MODELS)):
        if MODELS[next_model_index]["provider"] != selected_model_provider:
            # return the index of the next model
            return next_model_index

    # Return length of models so the while loop in get_ai_response stops 
    # when theres no other model to switch to.
    return len(MODELS)


def parse_ai_response(text: str) -> dict:
    """Parse the AI's JSON text output into a Python dictionary."""
    return json.loads(text)


def format_ai_output(ai_output: dict) -> dict:
    """Strip and uppercase every string field in the AI output except the
    2 explanations.

    Stripping turns blank emergency medicines (' ') into empty strings.
    Non string fields like ai_confidence_score are left unchanged.
    """
    explanation_fields = [
        "primary_diagnosis_explanation",
        "secondary_diagnosis_explanation",
    ]

    # For each field in AI output.
    for key, value in ai_output.items():
        # If the field is not an explanation field and is of type string,
        # then remove spaces at the start and end and uppercase them.
        if key not in explanation_fields and isinstance(value, str):
            ai_output[key] = value.strip().upper()

    return ai_output


# ======================================================================
# CORE FUNCTIONS
# ======================================================================
def get_ai_response(context: str, prompt: str, schema: dict) -> dict:
    """Try each model in MODELS until one returns a valid JSON reply.

    Errors are classified to decide whether to retry, switch model,
    switch provider or fail immediately. Returns an error dict if 
    nothing works before TOTAL_TIMEOUT_SECONDS runs out.
    """
    
    time_limit = time.time() + TOTAL_TIMEOUT_SECONDS
    current_model_index = 0
    current_retries = 0

    # While there is a model to select and the time limit has not been exceeded.
    while current_model_index < len(MODELS) and time.time() < time_limit:
        # Selects the current model to use and its name and provider.
        selected_model = MODELS[current_model_index]
        selected_model_provider = selected_model["provider"]
        selected_model_name = selected_model["model"]
        try:
            if selected_model_provider == "claude":
                ai_response = call_claude(selected_model_name, context, prompt, schema)
            elif selected_model_provider == "gemini":
                ai_response = call_gemini(selected_model_name, context, prompt, schema)

            # Unrecognised model name means switch to next model.
            else:
                print(f"{selected_model_provider} | {selected_model_name} "
                      f"unknown provider '{selected_model_provider}' -> skipping")
                current_model_index += 1
                continue

            ai_output = format_ai_output(parse_ai_response(ai_response))

            # ValueError is classified as RETRY_SAME_MODEL, so invalid ai output
            # fails validation and retries the same model, then switches model / provider
            # once retries run out, the same as other errors.
            if not validate_ai_output(ai_output):
                raise ValueError("AI output not found in the ICD11 / HSA datasets")

            return ai_output

        except Exception as error: 
            # Take an action based on the returned error.
            action = classify_error(error)
            print(f"{selected_model_provider} {selected_model_name} {error} -> {action}")

            # If fail then breaks the entire loop.
            if action == FAIL:
                break

            # If retry same model and retry limit is not exceeded.
            if action == RETRY_SAME_MODEL and current_retries < MAX_RETRIES_PER_MODEL:
                current_retries += 1

                # Typical retry logic is that time between retries
                # should increase as number of retries increase.
                # .sleep increases delay time between successive retries.
                time.sleep(current_retries)

                # This continue skips current_retries = 0 as we only
                # want retries to be reset upon changing models or model providers.
                continue

            # If switch model provider then set current model index to
            # the next available model provider.
            # If no next model provider is available then next_provider_index
            # returns the length of MODELS, which effectively stops
            # the main while loop from running as there are no more models to run.
            if action == SWITCH_MODEL_PROVIDER:
                current_model_index = next_provider_index(
                    current_model_index, selected_model_provider)

            elif action == SWITCH_MODEL or action == RETRY_SAME_MODEL:
                # RETRY_SAME_MODEL only reaches here once retries are used up
                current_model_index += 1

            # Handle unexpected errors.
            else:
                break

            # Reset retry count. It will only be reached when
            # action is SWITCH_MODEL or SWITCH_MODEL_PROVIDER.
            current_retries = 0

    # Unexpected error message
    return {"error": CONTACT_SUPPORT_MESSAGE}


def create_ai_prompt(ai_output: dict) -> str:
    """Build the patient intake prompt from the already filtered answers
    """
    ai_prompt = "Presenting patient answers:\n"

    for key, value in ai_output.items():
        ai_prompt += f"- {key}: {value}\n"

    return ai_prompt

def get_ai_output(answers_filtered: dict) -> dict:
    """Build the prompt from the filtered patient answers and return the
    validated AI output, or an error dict if every model failed."""
    ai_prompt = create_ai_prompt(answers_filtered)
    return get_ai_response(AI_MEDICAL_CONTEXT, ai_prompt, AI_OUTPUT_SCHEMA)


# ======================================================================
# AI OUTPUT VALIDATION FUNCTIONS
# ======================================================================
def validate_diagnosis(ai_diagnosis: str, ai_code: str) -> bool:
    """
    Check that an AI diagnosis title and its code are in the ICD11 dataset.

    Returns True only if the title and code are an exact match on the
    same row, so a real title paired with the wrong code fails.
    Expects the title and code to already be stripped and uppercased by
    format_ai_output.
    """

    # Go through DF_ICD11 one row at a time. The row number is used to get
    # the "Title" and "Code" from that same row. Return True as soon as the
    # ai_output diagnosis and code match on the same row.
    for row in range(len(VALID_DIAGNOSES)):
        valid_diagnosis = VALID_DIAGNOSES[row]
        valid_code = VALID_CODES[row]

        if ai_diagnosis == valid_diagnosis and ai_code == valid_code:
            return True

    return False


def validate_medicine(ai_medicine: str) -> bool:
    """
    Check that an AI medicine is in the HSA dataset.

    Returns True if the medicine is found inside any product name or
    active ingredient, e.g. 'Paracetamol' is found in
    'SUNNY PARACETAMOL TABLET 500 mg'. Returns False for an empty
    medicine. Expects the medicine to already be stripped and uppercased
    by format_ai_output.
    """

    # An empty medicine is never valid. This check is needed because ''
    # is found inside every dataset entry, so it would wrongly return True.
    if ai_medicine == "":
        return False

    # Return True as soon as the AI output medicine is contained in a
    # dataset entry, e.g. 'Paracetamol' in 'SUNNY PARACETAMOL TABLET 500 mg'.
    for medicine in VALID_MEDICINES:
        if ai_medicine in medicine:
            return True

    # else if AI output medicine not in the dataset then return False.
    return False


def validate_ai_output(ai_output: dict) -> bool:
    """
    Check the AI output against the ICD11 and HSA datasets.

    Validation passes in only 2 cases:
    1. Normal case: both diagnoses match the ICD-11 dataset AND all 4
       medicines match the HSA dataset.
    2. Emergency case: both diagnoses match the ICD11 dataset AND at
       least one explanation contains the word "EMERGENCY". The
       medicines are not checked because the AI is instructed to 
       leave them empty since its better for a doctor to decide in a
       real emergency as emergencies are complex.
    Everything else fails validation.
    """

    # Step 1: Check that both diagnoses and codes match the ICD11 dataset.
    # They return True if valid and False otherwise.
    primary_diagnosis_is_valid = validate_diagnosis(
        ai_output["primary_diagnosis_ICD11_Title"],
        ai_output["primary_diagnosis_ICD11_Code"],
    )
    secondary_diagnosis_is_valid = validate_diagnosis(
        ai_output["secondary_diagnosis_ICD11_Title"],
        ai_output["secondary_diagnosis_ICD11_Code"],
    )

    # Return False if either doesn't match. Only pass validation when
    # both primary and secondary diagnosis are valid.
    if not primary_diagnosis_is_valid or not secondary_diagnosis_is_valid:
        return False

    # Step 2: Collect the 4 medicine fields into a list so they can be
    # checked one at a time.
    medicines = [
        ai_output["primary_diagnosis_medicine_1"],
        ai_output["primary_diagnosis_medicine_2"],
        ai_output["secondary_diagnosis_medicine_1"],
        ai_output["secondary_diagnosis_medicine_2"],
    ]

    # Step 3: Count how many medicines match the HSA dataset.
    valid_medicine_count = 0

    for medicine in medicines:
        if validate_medicine(medicine):
            valid_medicine_count += 1

    # Case 1 (normal): all 4 medicines are valid and the 2 diagnosis match.
    if valid_medicine_count == 4:
        return True

    # Step 4: Check if either explanation contains the word "EMERGENCY".
    primary_explanation = ai_output["primary_diagnosis_explanation"]
    secondary_explanation = ai_output["secondary_diagnosis_explanation"]

    # Case 2 (emergency): the medicines didn't all match, but it is an
    # emergency so they are not needed.
    if "EMERGENCY" in primary_explanation or "EMERGENCY" in secondary_explanation:
        return True

    # Any other combination fails validation.
    return False