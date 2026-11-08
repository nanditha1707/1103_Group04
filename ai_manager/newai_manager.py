# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import httpx
import httpx2
import pandas as pd
from dotenv import load_dotenv

import logic_manager as logic
from ai_output import AiOutput
from ai_pipeline import AiPipeline
from claude_provider import ClaudeProvider
from error_classifier import ErrorClassifier
from gemini_provider import GeminiProvider

# Timeout for 1 AI API request.
REQUEST_TIMEOUT_SECONDS = 20
# Timeout for all API requests to return a valid answer. 
TOTAL_TIMEOUT_SECONDS = 60
# Retry number for retrying on same the same model.
MAX_RETRIES_PER_MODEL = 2
# Models to use for the AI API, in order of execution.
MODELS: list[dict[str, str]] = [
    {"provider": "claude", "model": "claude-opus-5-5"},
    {"provider": "claude", "model": "claude-sonnet-5-5"},
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.5-flash-lite"},
]

# Actions returned by classify_error, telling get_ai_response what to
# do after a failed request.
FAIL = "Fail immediately"
RETRY_SAME_MODEL = "Retry on the same model"
SWITCH_MODEL = "Switch to next model in MODELS"
SWITCH_MODEL_PROVIDER = "Switch immediately to the next model provider"
CONTACT_SUPPORT_MESSAGE = (
    "Please alert a nurse and proceed with manual regristration. "
    "Either an unexpected error has occured or all AI APIs are currently down. "
)

# Gemini raises raw httpx / httpx2 errors for timeouts and dropped
# connections, so both libraries are checked in classify_error.
GEMINI_TIMEOUT_ERRORS = (httpx.TimeoutException, httpx2.TimeoutException)
GEMINI_CONNECTION_ERRORS = (httpx.TransportError, httpx2.TransportError)
# Error message raised when the AI returns no text. classify_error checks
# for this exact message to tell it apart from other ValueErrors.
NO_TEXT_ERROR_MESSAGE = "AI returned no text"

# Every field the AI must return, used to build the JSON schema below.
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

# JSON schema both providers use to force the reply into AI_OUTPUT_FIELDS.
# additionalProperties False stops the AI adding fields of its own.
AI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": AI_OUTPUT_FIELDS,
    "required": list(AI_OUTPUT_FIELDS.keys()),
    "additionalProperties": False,
}

# System prompt sent with every request.
AI_MEDICAL_CONTEXT = """
You are a clinical decision support assistant at a primary care clinic in Singapore.
Your goal is to effectively and accurately triage patients based on the patient
details provided to you. Your output is reviewed by a certified medical professional
and is not a final diagnosis.

Task:
- Based on the patient's intake answers, suggest 2 diagnosis: 1 likely primary and 
  1 likely secondary diagnosis using ICD-11 titles and their respective codes.
- Suggest up to two suitable medicines for each diagnosis.

Diagnosis rules:
- Use the ICD-11 title exactly as written by the WHO. Do not shorten or reword titles.
- The code must be the exact code for that title in ICD-11.
- Your output is checked word for word against the ICD-11 MMS title list, so a single
  missing or extra word fails the check.
- ICD-11 titles often differ from ICD-10 titles. Never use ICD-10 wording. For example,
  CA07.0 is 'Acute upper respiratory infection, site unspecified', not
  'Acute upper respiratory infection, unspecified' (that is ICD-10 J06.9).
- If one of the common titles below fits the patient, copy it and its code exactly.
  Only use a title outside this list if you are certain of its exact ICD-11 wording.
  If you are unsure of a more specific title, use a broader parent title you are sure of.

Common primary care ICD-11 titles (code: title):
- CA07.0: Acute upper respiratory infection, site unspecified
- CA00: Acute nasopharyngitis
- CA02: Acute pharyngitis
- CA03: Acute tonsillitis
- CA01: Acute sinusitis
- CA08.0: Allergic rhinitis
- 1E32: Influenza, virus not identified
- CA42: Acute bronchitis
- CA40: Pneumonia
- CA23: Asthma
- 1D20: Dengue without warning signs
- 1D21: Dengue with warning signs
- 1A40: Gastroenteritis or colitis without specification of infectious agent
- DA42: Gastritis
- DA22: Gastro-oesophageal reflux disease
- MD92: Dyspepsia
- GC00: Cystitis
- GC08: Urinary tract infection, site not specified
- 8A80: Migraine
- 8A81: Tension-type headache
- ME84.2: Low back pain
- 9A60: Conjunctivitis
- AB00: Acute otitis media
- EA80: Atopic eczema
- 1E90: Varicella

Medicine rules:
- Each medicine field must be exactly one generic active ingredient name, as listed
  in the Singapore Health Sciences Authority (HSA) register of therapeutic products, or
  the product name as listed under HSA is also allowed.
- Use HSA spellings, e.g. 'Paracetamol' (not 'Acetaminophen'), 'Chlorpheniramine'
  (not 'Chlorphenamine'), 'Salbutamol' (not 'Albuterol').
- Do not include doses, strengths, salt forms, dosage forms, brand names, brackets,
  'e.g.', slashes, or conditions such as 'if within flu window'.
- Do not use drug classes (e.g. 'Antihistamine', 'Decongestant') or non-drug advice
  (e.g. 'Rest', 'Fluids', 'Supportive care').

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

# Actions the pipeline can take after a failed request, keyed by the names
# ErrorClassifier and AiPipeline use.
ACTIONS = {
    "fail": FAIL,
    "retry_same_model": RETRY_SAME_MODEL,
    "switch_model": SWITCH_MODEL,
    "switch_model_provider": SWITCH_MODEL_PROVIDER,
}

# Fields that hold free text, so they are not stripped and uppercased.
EXPLANATION_FIELDS = [
    "primary_diagnosis_explanation",
    "secondary_diagnosis_explanation",
]

# Reads API key from local .env file.
load_dotenv(override=True)

# ======================================================================
# FUNCTIONS CREATING OBJECTS
# ======================================================================
# keep original function names, parameters and return values.
# Apply to functions that are not class methods

# create a ClaudeProvider object with the following constants as its attributes.
def _claude_provider() -> ClaudeProvider:
    # underscore prefix for internal use only
    return ClaudeProvider(REQUEST_TIMEOUT_SECONDS, NO_TEXT_ERROR_MESSAGE)

# create a GeminiProvider object with the following constants as its attributes.
def _gemini_provider() -> GeminiProvider:
    # underscore prefix for internal use only
    return GeminiProvider(REQUEST_TIMEOUT_SECONDS, NO_TEXT_ERROR_MESSAGE)

# create an ErrorClassifier object with the following constants as its attributes.
def _error_classifier() -> ErrorClassifier:
    # underscore prefix for internal use only
    return ErrorClassifier(
        ACTIONS,
        NO_TEXT_ERROR_MESSAGE,
        GEMINI_TIMEOUT_ERRORS,
        GEMINI_CONNECTION_ERRORS
    )

# create an AiOutput object.
def _ai_output(
    icd_df: pd.DataFrame | None = None,
    hsa_df: pd.DataFrame | None = None
) -> AiOutput:
    # underscore prefix for internal use only
    return AiOutput(
        icd_df,
        hsa_df,
        logic.get_classification,
        EXPLANATION_FIELDS
    )

# create an AiPipeline object with the following constants as its attributes.
def _ai_pipeline(
    icd_df: pd.DataFrame | None = None,
    hsa_df: pd.DataFrame | None = None,
    context: str = AI_MEDICAL_CONTEXT,
    schema: dict = AI_OUTPUT_SCHEMA
) -> AiPipeline:
    # underscore prefix for internal use only
    return AiPipeline(
        MODELS,
        {
            "claude": _claude_provider(),
            "gemini": _gemini_provider()
        },
        _error_classifier(),
        _ai_output(icd_df, hsa_df),
        context,
        schema,
        ACTIONS,
        TOTAL_TIMEOUT_SECONDS,
        MAX_RETRIES_PER_MODEL,
        CONTACT_SUPPORT_MESSAGE
    )
# ======================================================================
# FUNCTIONS USING CLAUDEPROVIDER AND GEMINIPROVIDER CLASS METHODS
# ======================================================================
def call_gemini(model: str, context: str, prompt: str, schema: dict) -> str:
    """Send a prompt to Gemini and return its JSON reply as text.

    Gemini's timeout is in milliseconds, so timeout multiplied by 1000.

    'attempts' is set to 1 (the original request only, no retries)
    because it is better for the retries to be handled by the pipeline.
    """
    return _gemini_provider().call(model, context, prompt, schema)

def call_claude(model: str, context: str, prompt: str, schema: dict) -> str:
    """Send a prompt to Claude and return its JSON reply as text.

    'max_retries' is set to 0 because it is better for the retries to
    be handled by the pipeline.
    """
    return _claude_provider().call(model, context, prompt, schema)
# ======================================================================
# FUNCTIONS USING ERRORCLASSIFIER, AIPIPELINE AND AIOUTPUT CLASS METHODS
# ======================================================================
def classify_error(error: Exception) -> str:
    """Unified function to classify all API errors from Claude and
    Gemini. It classifies the error based on either the error code or
    for errors without error codes, the error itself, and returns a
    suitable ACTION (a constant) to take based on the error message.

    The Claude and Gemini error codes and their actions are listed in
    ErrorClassifier.classify.
    """
    return _error_classifier().classify(error)

def next_provider_index(current_model_index: int, selected_model_provider: str) -> int:
    """Return the index of the next model from a different provider."""
    return _ai_pipeline().next_provider_index(
        current_model_index,
        selected_model_provider
    )

def parse_ai_response(text: str) -> dict:
    """Parse the AI's JSON text output into a Python dictionary."""
    return AiOutput.parse(text)
# ======================================================================
# FUNCTIONS USING AIPIPELINE CLASS METHODS
# ======================================================================

# ======================================================================
# FUNCTIONS USING AIOUTPUT CLASS METHODS
# ======================================================================