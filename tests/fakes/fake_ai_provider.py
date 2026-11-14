from collections.abc import Iterable
from typing import override

from ai_manager import Action, AIProvider, AIRequest


class FakeAIProvider(AIProvider):
    def __init__(
        self, outcomes: Iterable[str | Exception], error_action: Action | None = None
    ) -> None:
        self.__outcomes = list(outcomes)
        self.__error_action = error_action
        self.__sent: list[tuple[str, AIRequest]] = []

    @property
    def models_sent(self) -> list[str]:
        return [model for model, _ in self.__sent]

    @property
    def requests(self) -> list[AIRequest]:
        return [request for _, request in self.__sent]

    @override
    def send(self, model: str, request: AIRequest) -> str:
        self.__sent.append((model, request))
        if not self.__outcomes:
            raise AssertionError(f"No scripted outcome left for the model: {model}")

        outcome = self.__outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    @override
    def classify_error(self, error: Exception) -> Action | None:
        """ModelFallback classifies every error, so a test that runs out of
        outcomes is raised here instead of being treated as an API error."""
        if isinstance(error, AssertionError):
            raise error
        return self.__error_action
