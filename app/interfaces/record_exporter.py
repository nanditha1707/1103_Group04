from typing import Protocol


class RecordExporter(Protocol):

    def export_record(self, all_user_responses: dict, ai_output: dict, logic_result: dict) -> str | None:
        pass
