import time
from collections.abc import Callable, Sequence
from .action import Action
from .ai_model import AIModel
from .ai_request import AIRequest
from .error_classifier import ErrorClassifier


class ModelFallback:
    """Sends a request to each model until one gives a reply that
    is accepted.

    After each failed attempt, ErrorClassifier decides whether to retry
    same model, move to the next model, skip the rest of that provider's
    models (switch model providers), or stop. It stops when it runs out 
    of models or time.

    It knows nothing about diagnoses. The caller passes a function that
    turns a reply into the final output, or raises an error if the reply
    is not acceptable, so it can be reused for any kind of request.
    """

    def __init__(
        self, models: Sequence[AIModel], classifier: ErrorClassifier, total_timeout: float, max_retries_per_model: int, sleep: Callable[[float], None] | None = None
    ):
        # Models to try, in order.
        self.__models = list(models)
        self.__classifier = classifier
        # Timeout for all attempts together, in seconds.
        self.__total_timeout = total_timeout
        # How many times the same model is retried before moving on.
        self.__max_retries_per_model = max_retries_per_model
        # Waits between retries. Tests pass in a function that does not
        # wait, so they run instantly.
        if sleep is not None:
            self.__sleep = sleep
        else:
            self.__sleep = time.sleep

    def run(
        self, request: AIRequest, read_reply: Callable[[str], dict]
    ) -> dict | None:
        """Return the output of the first accepted reply, or None if every
        model failed or the total timeout ran out.

        read_reply turns a reply into the output, and raises an error if
        the reply is not acceptable. That error is classified like an API
        error.
        """
        deadline = time.monotonic() + self.__total_timeout
        model_index = 0
        retries = 0

        # While there is a model to try and the time limit has not passed.
        while (
            model_index < len(self.__models)
            and time.monotonic() < deadline
        ):
            model = self.__models[model_index]

            try:
                reply = model.provider.send(model.name, request)
                return read_reply(reply)

            # Every error is classified instead of crashing the kiosk. 
            # Unexpected errors are classified as FAIL.
            except Exception as error:
                action = self.__classifier.classify(error, model.provider)

            if action is Action.FAIL:
                return None

            if (
                action is Action.RETRY_SAME_MODEL
                and retries < self.__max_retries_per_model
            ):
                retries += 1
                # Wait longer after each retry (1 seconds, then 2 seconds) to
                # handle transient errors. Usually for transient errors
                # more time is given between consecutive requests to give
                # time for the transient problem to go away. A basic version
                # of this is implemented here.
                self.__sleep(retries)
                continue

            model_index = self.__next_model_index(model_index, action)
            # A new model starts with no retries used.
            retries = 0

        return None

    def __next_model_index(self, model_index: int, action: Action) -> int:
        """Return the index of the model to try after the action."""
        if action is Action.SWITCH_PROVIDER:
            return self.__next_provider_index(model_index)

        # SWITCH_MODEL or RETRY_SAME_MODEL once its retries are used up.
        return model_index + 1

    def __next_provider_index(self, model_index: int) -> int:
        """Return the index of the next model from a different provider.

        Returns the length (number) of models if there is no next model
        to try. This ends the while loop in run() as model_index < len(self.__models)
        will become False.
        """
        provider = self.__models[model_index].provider

        for next_index in range(model_index + 1, len(self.__models)):
            if self.__models[next_index].provider is not provider:
                return next_index

        return len(self.__models)
