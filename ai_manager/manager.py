# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import pandas as pd
from dotenv import load_dotenv

import logic_manager as logic

from .ai_output import AiOutput
from .ai_pipeline import AiPipeline
from .claude_provider import ClaudeProvider
from .constants import (
    ACTIONS,
    AI_MEDICAL_CONTEXT,
    AI_OUTPUT_SCHEMA,
    CONTACT_SUPPORT_MESSAGE,
    EXPLANATION_FIELDS,
    GEMINI_CONNECTION_ERRORS,
    GEMINI_TIMEOUT_ERRORS,
    MAX_RETRIES_PER_MODEL,
    MODELS,
    NO_TEXT_ERROR_MESSAGE,
    REQUEST_TIMEOUT_SECONDS,
    TOTAL_TIMEOUT_SECONDS,
)
from .error_classifier import ErrorClassifier
from .gemini_provider import GeminiProvider

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

def format_ai_output(ai_output: dict) -> dict:
    """Strip and uppercase every string field in the AI output except the
    2 explanations.

    Stripping turns blank emergency medicines (' ') into empty strings.
    Non string fields like ai_confidence_score are left unchanged.
    """
    return _ai_output().format(ai_output)
# ======================================================================
# FUNCTIONS USING AIPIPELINE CLASS METHODS
# ======================================================================
def get_ai_response(
    context: str,
    prompt: str,
    schema: dict,
    icd_df: pd.DataFrame,
    hsa_df: pd.DataFrame | None
) -> dict:
    """Try each model in MODELS until one returns a valid JSON reply.

    Errors are classified to decide whether to retry, switch model,
    switch provider or fail immediately. Returns an error dict if
    nothing works before TOTAL_TIMEOUT_SECONDS runs out.
    """
    return _ai_pipeline(icd_df, hsa_df, context, schema).get_response(prompt)

def create_ai_prompt(answers_filtered: dict) -> str:
    """Build the patient intake prompt from the already filtered answers,
    with one "- key: value" line per answer."""
    return AiPipeline.create_prompt(answers_filtered)

def get_ai_output(
    answers_filtered: dict,
    icd_df: pd.DataFrame | None,
    hsa_df: pd.DataFrame | None
) -> dict:
    """Build the prompt from the filtered patient answers and return the
    validated AI output, or an error dict if every model failed.

    icd_df and hsa_df are the cleaned datasets loaded by data_manager.
    hsa_df is the same one logic_manager routes with, so every medicine
    that passes validation has a classification."""
    return _ai_pipeline(icd_df, hsa_df).get_output(answers_filtered)

# ======================================================================
# FUNCTIONS USING AIOUTPUT CLASS METHODS
# ======================================================================
def validate_diagnosis(ai_diagnosis: str, ai_code: str, icd_df: pd.DataFrame) -> bool:
    """
    Check that an AI diagnosis title and its code are in the cleaned
    ICD11 dataset.

    Returns True only if the title and code are an exact match on the
    same row, so a real title paired with the wrong code fails.
    Expects the title and code to already be stripped and uppercased by
    format_ai_output, the same as the cleaned dataset.
    """
    return _ai_output(icd_df).validate_diagnosis(ai_diagnosis, ai_code)

def validate_medicine(ai_medicine: str, hsa_df: pd.DataFrame) -> bool:
    """
    Check that an AI medicine is in the cleaned HSA dataset.

    Returns True if the medicine is found inside any product name or
    active ingredient, e.g. 'PARACETAMOL' is found in
    'SUNNY PARACETAMOL TABLET 500 MG'. Returns False for an empty
    medicine. Expects the medicine to already be stripped and uppercased
    by format_ai_output.

    Uses the same lookup as logic_manager's routing, so a medicine that
    passes validation always has an HSA classification to route with.
    """
    return _ai_output(hsa_df=hsa_df).validate_medicine(ai_medicine)

def validate_ai_output(
    ai_output: dict, icd_df: pd.DataFrame, hsa_df: pd.DataFrame | None
) -> bool:
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
    return _ai_output(icd_df, hsa_df).validate(ai_output)
