import time

from ai_output import AiOutput
from ai_provider import AiProvider
from error_classifier import ErrorClassifier


class AiPipeline:
    """Builds the prompt, sends it through the models in order and
    returns the first valid AI output."""

    def __init__(
        self,
        models: list[dict[str, str]],
        providers: dict[str, AiProvider],
        classifier: ErrorClassifier,
        ai_output: AiOutput,
        context: str,
        schema: dict,
        actions: dict[str, str],
        total_timeout: int,
        max_retries_per_model: int,
        support_message: str
    ):
        # Models to use for the AI API, in order of execution.
        self.__models = models
        # Maps each provider name in models to its AiProvider.
        self.__providers = providers
        self.__classifier = classifier
        self.__ai_output = ai_output
        self.__context = context
        self.__schema = schema
        # Actions returned by classify_error, telling get_ai_response what to
        # do after a failed request.
        self.__actions = actions
        # Timeout for all API requests to return a valid answer.
        self.__total_timeout = total_timeout
        # Retry number for retrying on same the same model.
        self.__max_retries_per_model = max_retries_per_model
        self.__support_message = support_message

    def next_provider_index(
        self,
        current_model_index: int,
        selected_model_provider: str
    ) -> int:
        """Return the index of the next model from a different provider."""

        for next_model_index in range(current_model_index + 1, len(self.__models)):
            if self.__models[next_model_index]["provider"] != selected_model_provider:
                # return the index of the next model
                return next_model_index

        # Return length of models so the while loop in get_ai_response stops 
        # when theres no other model to switch to.
        return len(self.__models)