from typing import Protocol


class PatientRouter(Protocol):

    def process_result(self, ai_output: dict) -> dict:
        pass
