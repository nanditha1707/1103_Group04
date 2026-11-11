import pandas as pd
from ai_manager.providers import ClaudeProvider, GeminiProvider
from . import constants
from .ai_model import AIModel
from .error_classifier import ErrorClassifier
from .manager import AIManager
from .model_fallback import ModelFallback
from .output_validator import OutputValidator
from .prompt_builder import PromptBuilder
from .reply_parser import ReplyParser


class AIManagerFactory:
    """Builds the AIManager that main.py uses.

    This is the only class that creates the concrete providers, such as
    ClaudeProvider and GeminiProvider, and the only one that reads the
    models, timeouts and prompt in constants.py. AIManager is given every
    object it needs instead so it does not depend on any provider.

    A new provider is a new AIProvider subclass plus one line in the
    providers list in __create_fallback below, with no change to AIManager
    or ModelFallback.
    """

    @staticmethod
    def create(icd_df: pd.DataFrame | None, hsa_df: pd.DataFrame | None) -> AIManager:
        """Return an AIManager that checks every reply against the cleaned
        ICD-11 and HSA datasets. Either can be None if it failed to load.
        """
        return AIManager(
            PromptBuilder(constants.AI_MEDICAL_CONTEXT, constants.AI_OUTPUT_SCHEMA),
            ReplyParser(),
            OutputValidator(icd_df, hsa_df),
            AIManagerFactory.__create_fallback()
        )

    @staticmethod
    def __create_fallback() -> ModelFallback:
        """Return the ModelFallback that tries each provider's models in
        the order of the providers list below.

        Example of what it returns with the current constants, where claude
        is one ClaudeProvider(20) and gemini is one GeminiProvider(20):

            ModelFallback(
                models=[
                    AIModel(claude, "claude-opus-5-5"),
                    AIModel(claude, "claude-sonnet-5-5"),
                    AIModel(gemini, "gemini-3.8-flash"),
                    AIModel(gemini, "gemini-3.5-flash-lite"),
                ],
                classifier=ErrorClassifier(),
                total_timeout=60,
                max_retries_per_model=2,
            )

        AIManager.get_ai_output sends each request through its run().
        run() sends the request to claude-opus-5-5 first and returns the
        checked output dict from the first reply AIManager accepts. E.g. if
        Opus is overloaded (error 529) and Sonnet's reply is valid, run()
        returns Sonnet's output. It returns None if every model fails or 60
        seconds pass, and get_ai_output then returns
        {"error": CONTACT_SUPPORT_MESSAGE}.
        """
        timeout = constants.REQUEST_TIMEOUT_SECONDS

        # Claude models are tried first before Gemini models. Order can
        # be changed here. Each provider is created by name, so a new
        # provider's constructor can take whatever arguments it needs.
        providers = (
            (ClaudeProvider(timeout), constants.CLAUDE_MODELS),
            (GeminiProvider(timeout), constants.GEMINI_MODELS),
        )

        models = []
        for provider, model_names in providers:
            # One object per provider shared by its models so that
            # ModelFallback can tell which models belong to the same provider.
            models += [AIModel(provider, name) for name in model_names]

        return ModelFallback(
            models,
            ErrorClassifier(),
            constants.TOTAL_TIMEOUT_SECONDS,
            constants.MAX_RETRIES_PER_MODEL
        )
