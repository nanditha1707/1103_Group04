import time
from collections.abc import Callable, Sequence

from .action import Action
from .ai_model import AIModel
from .ai_request import AIRequest
from .error_classifier import ErrorClassifier


class ModelFallback:
    def __init__(
        self, models: Sequence[AIModel], classifier: ErrorClassifier, total_timeout: float, max_retries_per_model: int, sleep: Callable[[float], None] | None = None
    ):
        self.__models = list(models)
        self.__classifier = classifier
        self.__total_timeout = total_timeout
        self.__max_retries_per_model = max_retries_per_model
        self.__sleep = sleep if sleep is not None else time.sleep

    def run(
        self,
        request: AIRequest,
        read_reply: Callable[[str], dict]
    ) -> dict | None:
        deadline = time.monotonic() + self.__total_timeout
        model_index = 0
        retries = 0

        while (
            model_index < len(self.__models)
            and time.monotonic() < deadline
        ):
            model = self.__models[model_index]

            try:
                reply = model.provider.send(model.name, request)
                return read_reply(reply)

            except Exception as error:  # pylint: disable=broad-exception-caught
                action = self.__classifier.classify(error, model.provider)

            if action is Action.FAIL:
                return None

            if (
                action is Action.RETRY_SAME_MODEL
                and retries < self.__max_retries_per_model
            ):
                retries += 1
                self.__sleep(retries)
                continue

            model_index = self.__next_model_index(model_index, action)
            retries = 0

        return None

    def __next_model_index(self, model_index: int, action: Action) -> int:
        if action is Action.SWITCH_PROVIDER:
            return self.__next_provider_index(model_index)

        return model_index + 1

    def __next_provider_index(self, model_index: int) -> int:
        provider = self.__models[model_index].provider

        for next_index in range(model_index + 1, len(self.__models)):
            if self.__models[next_index].provider is not provider:
                return next_index

        return len(self.__models)
