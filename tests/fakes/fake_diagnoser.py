from typing import override

from app.interfaces import DiagnosisSource


class FakeDiagnoser(DiagnosisSource):
    def __init__(
        self, ai_output: dict
    ) -> None:
        self.__ai_output = ai_output
        self.__received: list[dict] = []

    @property
    def received(self) -> list[dict]:
        return list(self.__received)

    @override
    def get_ai_output(self, answers_filtered: dict) -> dict:
        self.__received.append(answers_filtered)
        return dict(self.__ai_output)
