from collections.abc import Callable

import pandas as pd

from ai_manager.providers import ClaudeProvider, GeminiProvider

from . import constants
from .ai_model import AIModel
from .error_classifier import ErrorClassifier
from .invalid_output_error import InvalidOutputError
from .model_fallback import ModelFallback
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
        self, icd_df: pd.DataFrame | None, hsa_df: pd.DataFrame | None, classify_medicine: Callable[[str, pd.DataFrame], str | None], fallback: ModelFallback | None = None
    ):
        self.__prompt_builder = PromptBuilder(
            constants.AI_MEDICAL_CONTEXT,
            constants.AI_OUTPUT_SCHEMA
        )
        self.__parser = ReplyParser()
        # main.py passes in logic_manager's medicine lookup, so a medicine
        # that passes validation always has a classification to route with.
        self.__validator = OutputValidator(icd_df, hsa_df, classify_medicine)

        if fallback is None:
            fallback = self.__default_fallback()
        self.__fallback = fallback

    def get_ai_output(self, answers_filtered: dict) -> dict:
        """Return the validated AI output for the filtered patient answers.

        Returns {"error": message} if the ICD-11 dataset did not load, or
        if no model gave a valid answer before the total timeout.
        """
        # Without ICD data the diagnoses cannot be checked, so the AI is not
        # called and the patient is sent to manual registration.
        if not self.__validator.has_icd_data:
            return {"error": constants.CONTACT_SUPPORT_MESSAGE}

        request = self.__prompt_builder.build(answers_filtered)
        output = self.__fallback.run(request, self.__read_reply)

        if output is None:
            return {"error": constants.CONTACT_SUPPORT_MESSAGE}

        return output

    def __read_reply(self, reply: str) -> dict:
        output = self.__parser.parse(reply)

        if not self.__validator.is_valid(output):
            raise InvalidOutputError(
                "AI output not found in the ICD11 / HSA datasets"
            )

        return output

    @staticmethod
    def __default_fallback() -> ModelFallback:
        claude = ClaudeProvider(constants.REQUEST_TIMEOUT_SECONDS)
        gemini = GeminiProvider(constants.REQUEST_TIMEOUT_SECONDS)

        models = [AIModel(claude, name) for name in constants.CLAUDE_MODELS]
        models += [AIModel(gemini, name) for name in constants.GEMINI_MODELS]

        return ModelFallback(
            models,
            ErrorClassifier(),
            constants.TOTAL_TIMEOUT_SECONDS,
            constants.MAX_RETRIES_PER_MODEL
        )
