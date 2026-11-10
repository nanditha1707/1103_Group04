import time

from .action import Action
from .ai_provider import AIProvider
from .ai_request import AIRequest
from .error_classifier import ErrorClassifier
from .invalid_output_error import InvalidOutputError
from .output_validator import OutputValidator
from .prompt_builder import PromptBuilder
from .reply_parser import ReplyParser


class AiPipeline:
    """Builds the prompt, sends it through the models in order and
    returns the first valid AI output."""

    def __init__(
        self, models: list[dict[str, str]], providers: dict[str, AIProvider], classifier: ErrorClassifier, prompt_builder: PromptBuilder, parser: ReplyParser, validator: OutputValidator, total_timeout: int, max_retries_per_model: int, support_message: str
    ):
        # Models to use for the AI API, in order of execution.
        self.__models = models
        # Maps each provider name in models to its AIProvider.
        self.__providers = providers
        self.__classifier = classifier
        self.__parser = parser
        self.__validator = validator
        self.__prompt_builder = prompt_builder
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

    def get_response(self, request: AIRequest) -> dict:
        """Try each model in MODELS until one returns a valid JSON reply.

        Errors are classified to decide whether to retry, switch model,
        switch provider or fail immediately. Returns an error dict if
        nothing works before TOTAL_TIMEOUT_SECONDS runs out.
        """
        time_limit = time.time() + self.__total_timeout
        current_model_index = 0
        current_retries = 0

        # While there is a model to select and the time limit has not been exceeded.
        while (
            current_model_index < len(self.__models)
            and time.time() < time_limit
        ):
            # Selects the current model to use and its name and provider.
            selected_model = self.__models[current_model_index]
            selected_model_provider = selected_model["provider"]
            selected_model_name = selected_model["model"]
            provider = self.__providers.get(selected_model_provider)

            # Unrecognised model name means switch to next model.
            if provider is None:
                current_model_index += 1
                continue

            try:
                ai_response = provider.send(selected_model_name, request)

                ai_output = self.__parser.parse(ai_response)

                # ValueError is classified as RETRY_SAME_MODEL, so invalid ai output
                # fails validation and retries the same model, then switches model / provider
                # once retries run out, the same as other errors.
                if not self.__validator.is_valid(ai_output):
                    raise InvalidOutputError(
                        "AI output not found in the ICD11 / HSA datasets"
                    )

                return ai_output

            except Exception as error:
                # Take an action based on the returned error. The provider
                # is passed in because only it knows its own SDK's errors.
                action = self.__classifier.classify(error, provider)

                # If fail then breaks the entire loop.
                if action is Action.FAIL:
                    break

                # If retry same model and retry limit is not exceeded.
                if (
                    action is Action.RETRY_SAME_MODEL
                    and current_retries < self.__max_retries_per_model
                ):
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
                if action is Action.SWITCH_PROVIDER:
                    current_model_index = self.next_provider_index(
                        current_model_index, selected_model_provider)

                elif action is Action.SWITCH_MODEL or action is Action.RETRY_SAME_MODEL:
                    # RETRY_SAME_MODEL only reaches here once retries are used up
                    current_model_index += 1

                # Handle unexpected errors.
                else:
                    break

                # Reset retry count. It will only be reached when
                # action is SWITCH_MODEL or SWITCH_PROVIDER.
                current_retries = 0

        # Unexpected error message
        return {"error": self.__support_message}
    
    def get_output(self, answers_filtered: dict) -> dict:
        """Build the prompt from the filtered patient answers and return the
        validated AI output, or an error dict if every model failed.

        icd_df and hsa_df are the cleaned datasets loaded by data_manager.
        hsa_df is the same one logic_manager routes with, so every medicine
        that passes validation has a classification."""

        # Without ICD data the diagnoses cannot be checked, so the AI is not
        # called and the patient is sent to manual registration.
        if not self.__validator.has_icd_data:
            return {"error": self.__support_message}

        request = self.__prompt_builder.build(answers_filtered)
        return self.get_response(request)