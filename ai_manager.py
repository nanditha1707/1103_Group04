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
import pandas as pd
from google.genai import errors as genai_errors

FAIL = "Fail immediately"
RETRY_SAME_MODEL = "Retry on the same model"
SWITCH_MODEL = "Switch models"
SWITCH_MODEL_PROVIDER = "Switch immediately to a different model provider"
GEMINI_TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
GEMINI_CONNECTION_ERRORS = (httpx.ConnectError, httpx2.ConnectError)
REQUEST_TIMEOUT_SECONDS = 20
TOTAL_TIMEOUT_SECONDS = 60
MAX_RETRIES_PER_MODEL = 3
CONTACT_SUPPORT_MESSAGE = (
    "Please contact technical staff for assistance. "
    "Either an unexpected error has occured or all AI APIs are currently down. "
)

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
    "refused":{"type":"string"}
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
- If you can give a valid answer, set "refused" to "False".
- If you cannot give a valid answer to the prompt, set "refused" to "True", set
  ai_confidence_score to 0, and make all other fields empty strings.

Symptom definitions:
- 'high fever' means a temperature at or above 39 degrees Celsius.
- 'fever' means a temperature below 39 degrees Celsius.

Medicine selection:
- When choosing between medicines with very similar attributes and effects, pick the
  one that is easier to access.
- Accessibility from most to least accessible: retail -> pharmacy only ->
  prescription only.
- Reason: this triage aims to divert patients away from overcrowded healthcare
  facilities. Patients are routed to a retail store, pharmacist or doctor based on
  whether the medicine is available at retail, pharmacy only or prescription only."""

MODELS = [
    {"provider": "claude", "model": "claude-opus-5-5"},
    {"provider": "claude", "model": "claude-sonnet-5"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
]

FILE_PATH_ICD11 = "datasets/icd11.csv"
FILE_PATH_HSA = "datasets/hsa.csv"
DF_ICD11 = pd.read_csv(FILE_PATH_ICD11)
DF_HSA = pd.read_csv(FILE_PATH_HSA)
DATASET_DIAGNOSIS = DF_ICD11["Title"].str.upper()
DATASET_CODE = DF_ICD11["Code"].str.upper()
DATASET_MEDICINE = pd.concat(
    [DF_HSA["Productname"], DF_HSA["Activeingredients"]]
).str.upper()

# Reads API key from local .env file.
load_dotenv()


# ======================================================================
# API CALL FUNCTIONS
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
# ERROR CLASSIFICATION FUNCTIONS
# ======================================================================


def classify_error(error):
    """Unified function to classify all API errors from Claude and
    Gemini. It classifies the error based on either the error code or
    for errors without error codes, the error itself, and returns a
    suitable action to take based on the error message."""

    # Something wrong with json generation, or AI output failed validation
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

            ai_output = parse_ai_response(ai_response)

            # ValueError is classified as RETRY_SAME_MODEL, so invalid output
            # retries the same model, then switches model / provider once
            # retries run out, the same as other errors.
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

            elif action in (SWITCH_MODEL, RETRY_SAME_MODEL):
                # RETRY_SAME_MODEL only reaches here once retries are used up
                current_model_index += 1

            else:
                # Handle unexpected errors.
                break

            # Reset retry count. It will only be reached when
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


# ======================================================================
# AI VALIDATION FUNCTIONS
# ======================================================================


def validate_diagnosis_code(diagnosis: str, code: str, label: str) -> bool:
    """The validate_diagnosis_code() function stores the input of 
    three string values named diagnosis, code and label (diagnosis) 
    represent the dictionary(ai_output) value of the diagnosis
    (code) represents the dictionary(ai_output) value of the code 
    (label) represents the level(primary/secondary) of the output 
    Returns True only if the diagnosis and code are found together
    on the same row of the dataset, and prints the result."""

    # False boolean value remains in isvalid_diagnosis_code unless the
    # ai_output diagnosis and code match the "Title" and "Code" columns
    # on the same row of DF_ICD11.
    isvalid_diagnosis_code = False

    # Go through DF_ICD11 one row at a time. The row number is used to get
    # the "Title" and "Code" from that same row.
    for row in range(len(DATASET_DIAGNOSIS)):
        valid_diagnosis = DATASET_DIAGNOSIS[row]
        valid_code = DATASET_CODE[row]

        if diagnosis.upper() == valid_diagnosis and code.upper() == valid_code:
            isvalid_diagnosis_code = True
            break

    return isvalid_diagnosis_code


def validate_medicine(medicine: str, label: str) -> bool:
    """
    This function has the same concept as validate_diagnosis_code() 
    function but it is to validate medicine instead of disease."""

    isvalid_medicine = False

    # If AI output medicine is contained in a dataset entry, e.g.
    # 'Paracetamol' in 'SUNNY PARACETAMOL TABLET 500 mg', then set
    # isvalid_medicine flag to True. Else it stays as False.
    for valid_medicine in DATASET_MEDICINE:
        if medicine.upper() in valid_medicine:
            isvalid_medicine = True
            break

    return isvalid_medicine


def validate_ai_output(ai_output: dict) -> bool:
    """Return True only if the AI did not refuse, every diagnosis title
    and code is found together in the ICD11 dataset and every medicine
    is found in the HSA dataset. Empty secondary diagnosis and medicine
    fields are skipped, as the AI is allowed to leave them empty."""
    if ai_output["refused"].upper() == "TRUE":
        return False

    for label in ("primary", "secondary"):
        diagnosis = ai_output[f"{label}_diagnosis_ICD11_Title"]
        code = ai_output[f"{label}_diagnosis_ICD11_Code"]

        # The primary diagnosis must always be checked. The secondary
        # diagnosis is optional, so it is only checked if the AI gave
        # a title or code for it.
        if label == "primary" or diagnosis != "" or code != "":
            isvalid_diagnosis = validate_diagnosis_code(diagnosis, code, label)
            if not isvalid_diagnosis:
                return False

        for medicine in (ai_output[f"{label}_diagnosis_medicine_1"],
                         ai_output[f"{label}_diagnosis_medicine_2"]):
            if medicine and not validate_medicine(medicine, label):
                return False

    return True