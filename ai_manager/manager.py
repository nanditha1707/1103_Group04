from collections.abc import Callable

import pandas as pd

from ai_manager.providers import ClaudeProvider, GeminiProvider

from . import constants
from .ai_model import AIModel
from .ai_pipeline import AiPipeline
from .error_classifier import ErrorClassifier
from .output_validator import OutputValidator
from .prompt_builder import PromptBuilder
from .reply_parser import ReplyParser


class AIManager:
    """The class main.py uses to get a diagnosis from the AI.

    It builds the objects that do the work once, when the program starts,
    instead of on every call:
    - ClaudeProvider and GeminiProvider send requests to their APIs, and
      classify their own SDK's errors.
    - ErrorClassifier decides what to do after a failed request.
    - AiOutput parses, formats and validates a reply.
    - AiPipeline tries each model in turn until one gives a valid reply.
    """

    def __init__(
        self, icd_df: pd.DataFrame | None, hsa_df: pd.DataFrame | None, classify_medicine: Callable[[str, pd.DataFrame], str | None]
    ):
        claude = ClaudeProvider(constants.REQUEST_TIMEOUT_SECONDS)
        gemini = GeminiProvider(constants.REQUEST_TIMEOUT_SECONDS)

        models = [AIModel(claude, name) for name in constants.CLAUDE_MODELS]
        models += [AIModel(gemini, name) for name in constants.GEMINI_MODELS]

        classifier = ErrorClassifier()
        prompt_builder = PromptBuilder(
            constants.AI_MEDICAL_CONTEXT,
            constants.AI_OUTPUT_SCHEMA
        )
        parser = ReplyParser()
        # main.py passes in logic_manager's medicine lookup, so a medicine
        # that passes validation always has a classification to route with.
        validator = OutputValidator(icd_df, hsa_df, classify_medicine)

        self.__pipeline = AiPipeline(
            models,
            classifier,
            prompt_builder,
            parser,
            validator,
            constants.TOTAL_TIMEOUT_SECONDS,
            constants.MAX_RETRIES_PER_MODEL,
            constants.CONTACT_SUPPORT_MESSAGE
        )

    def get_ai_output(self, answers_filtered: dict) -> dict:
        """Return the validated AI output for the filtered patient answers.

        Returns {"error": message} if the ICD-11 dataset did not load, or
        if no model gave a valid answer before the total timeout.
        """
        return self.__pipeline.get_output(answers_filtered)
