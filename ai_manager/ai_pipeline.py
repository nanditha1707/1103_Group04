import time

from .ai_output import AiOutput
from .ai_provider import AiProvider
from .error_classifier import ErrorClassifier


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
    
    @staticmethod
    def create_prompt(answers_filtered: dict) -> str:
        """Build the patient intake prompt from the already filtered answers,
        with one "- key: value" line per answer."""
        ai_prompt = "Presenting patient answers:\n"

        for key, value in answers_filtered.items():
            ai_prompt += f"- {key}: {value}\n"

        return ai_prompt
    
    def get_response(self, prompt: str) -> dict:
        """Try each model in MODELS until one returns a valid JSON reply.

        Errors are classified to decide whether to retry, switch model,
        switch provider or fail immediately. Returns an error dict if
        nothing works before TOTAL_TIMEOUT_SECONDS runs out.
        """
        fail = self.__actions["fail"]
        retry_same_model = self.__actions["retry_same_model"]
        switch_model = self.__actions["switch_model"]
        switch_model_provider = self.__actions["switch_model_provider"]

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
            try:
                provider = self.__providers.get(selected_model_provider)

                # Unrecognised model name means switch to next model.
                if provider is None:
                    current_model_index += 1
                    continue

                ai_response = provider.call(
                    selected_model_name,
                    self.__context,
                    prompt,
                    self.__schema
                )

                ai_output = self.__ai_output.format(
                    self.__ai_output.parse(ai_response)
                )

                # ValueError is classified as RETRY_SAME_MODEL, so invalid ai output
                # fails validation and retries the same model, then switches model / provider
                # once retries run out, the same as other errors.
                if not self.__ai_output.validate(ai_output):
                    raise ValueError(
                        "AI output not found in the ICD11 / HSA datasets"
                    )

                return ai_output

            except Exception as error:
                # Take an action based on the returned error.
                action = self.__classifier.classify(error)

                # If fail then breaks the entire loop.
                if action == fail:
                    break

                # If retry same model and retry limit is not exceeded.
                if (
                    action == retry_same_model
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
                if action == switch_model_provider:
                    current_model_index = self.next_provider_index(
                        current_model_index, selected_model_provider)

                elif action == switch_model or action == retry_same_model:
                    # RETRY_SAME_MODEL only reaches here once retries are used up
                    current_model_index += 1

                # Handle unexpected errors.
                else:
                    break

                # Reset retry count. It will only be reached when
                # action is SWITCH_MODEL or SWITCH_MODEL_PROVIDER.
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
        if not self.__ai_output.has_icd_data():
            return {"error": self.__support_message}

        ai_prompt = self.create_prompt(answers_filtered)
        return self.get_response(ai_prompt)