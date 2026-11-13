from typing import Protocol


class DiagnosisSource(Protocol):

    def get_ai_output(self, answers_filtered: dict) -> dict:
        pass
