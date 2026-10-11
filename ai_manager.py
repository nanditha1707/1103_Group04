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
MAX_RETRIES_PER_MODEL = 2
CONTACT_SUPPORT_MESSAGE = (
    "Please contact technical staff for assistance. "
    "Either an unexpected error has occured or all AI APIs are currently down. "
)

REQUEST_TIMEOUT_SECONDS = 20
TOTAL_TIMEOUT_SECONDS = 60
MAX_RETRIES_PER_MODEL = 3

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

AI_MEDICAL_CONTEXT = """You are a clinical decision support assistant at a primary care clinic in Singapore. The goal is to effectively
and accurately triage patients based on the patient details that will be provided to you.
Based on the patient's intake answers, suggest a likely primary and secondary diagnosis using ICD-11 titles and codes,
and up to two commonly used medicines for each diagnosis. Briefly explain the reasoning behind each diagnosis
under primary_diagnosis_explanation and secondary_diagnosis_explanation, your reasoning will be shown to 
mainly patients patients but also doctors, so do not use complex medical terms.
Your explanation should not be more than 120 characters per field.
Strictly list your explanations only in the primary_diagnosis_explanation and secondary_diagnosis_explanation 
fields and not elsewhere.
If there is no reasonable secondary diagnosis, use an empty string for the secondary diagnosis and medicine fields.
ai_confidence_score is an integer from 0 to 100 showing how confident you are in the primary diagnosis.
If you cannot give a valid answer then set "refused" field in the output to True and make all other fields empty.
If you can give a valid answer set "refused" field to False.
The difference between 'fever' and 'high fever' as symptoms is that 'high fever' is a fever at or above
39 degrees celcius while 'fever' is below it.
If you are deciding between medication with very similar attributes and effects, pick the one that is easier
to access; prescription -> pharmacy only -> retail in decreasing order of accessibility. The reason is because
this triaging is meant to divert patients away from overcrowded healthcare facilities, and the routing of patients
to a doctor / pharmacist / retail store is determined by the type of drug precribed and whether it is prescription
only, pharmacist only, or available at retail stores.
Your output is reviewed by a certified medical professional and is not a final diagnosis."""

MODELS = [
    {"provider": "claude", "model": "claude-opus-5-5"},
    {"provider": "claude", "model": "claude-sonnet-5"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
]


FILE_PATH_ICD11 = "datasets/icd_11.csv"
FILE_PATH_HSA = "datasets/ListingofRegisteredTherapeuticProducts.csv"
df1 = pd.read_csv(FILE_PATH_ICD11)
df2 = pd.read_csv(FILE_PATH_HSA)

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

# ======================================================================
# AI VALIDATION FUNCTIONS
# ======================================================================

# Two series with the column names "Title" and "Code" 
# is pulled from the ICD11 dataset.
dataset_diagnosis = df1["Title"].str.upper()
dataset_code = df1["Code"].str.upper()

# The pandas series with the column name "Productname" 
# is pulled from the HSA medicine dataset.
dataset_medicine = df2["Productname"].str.lower()

def validate_diagnosis_code(diagnosis: str, code: str, label: str) -> bool:
    """The validate_diagnosis_code() function stores the input of 
    three string values named diagnosis, code and label (diagnosis) 
    represent the dictionary(ai_output) value of the diagnosis
    (code) represents the dictionary(ai_output) value of the code 
    (label) represents the level(primary/secondary) of the output 
    Additionally, the result of which output is in the dataset 
    and/or which output is not in the dataset is printed."""

    # False boolean value remains in isvalid_code unless the ai_output 
    # code value finds a match in the "Code" column of df1.
    isvalid_code = False

    for valid_code in dataset_code:
        if code.upper() == valid_code.upper():
            isvalid_code = True
            break

    # False boolean value remains in isvalid_diagnosis unless the 
    # ai_output value finds a match in the "Title" column of df1.
    isvalid_diagnosis = False

    for valid_diagnosis in dataset_diagnosis:
       if diagnosis.upper() == valid_diagnosis.upper():
            isvalid_diagnosis = True
            break

    # Prints the result of a valid match.
    # Else it will indicate which specific data is not found.
    if isvalid_code and isvalid_diagnosis:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are found in the dataset.")
    elif isvalid_diagnosis:
        print(f"The {label} diagnosis: '{diagnosis}' is found in the dataset but the {label} code: '{code}' is not found.")
    elif isvalid_code:
        print(f"The {label} code: '{code}' is found in the dataset but the {label} diagnosis: '{diagnosis}' is not found.")
    else:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are not found in the dataset.")

    return isvalid_code, isvalid_diagnosis


def validate_medicine(medicine: str, label: str) -> bool:
    """
    This function has the same concept as validate_diagnosis_code() 
    function but it is to validate medicine instead of disease."""

    isvalid_medicine = False

    # If AI output medicine is in the dataset then set isvalid_medicine
    # flag to True. Else it stays as False.
    for valid_medicine in dataset_medicine:
        if medicine.upper() == valid_medicine.upper():
            isvalid_medicine = True
            break
    
    if isvalid_medicine:
        print(f"The {label} medicine: '{medicine}' is found in the dataset.")
    else:
        print(f"The {label} medcine: '{medicine}'is not found in the dataset.")

    return isvalid_medicine