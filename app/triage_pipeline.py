from ai_manager import AIManager
from app import constants
from data_manager import DataManager
from io_manager import IOManager
from io_manager.patient_answers import Answer
from logic_manager import LogicManager


class TriagePipeline:

    def __init__(
        self, io: IOManager, ai: AIManager, logic: LogicManager, data: DataManager
    ) -> None:
        self.__io = io
        self.__ai = ai
        self.__logic = logic
        self.__data = data

    def process(self, answers: dict[str, Answer]) -> None:
        # Filter answers so only non-personal information goes to the AI.
        answers_filtered = self.__io.filter_for_ai(answers)

        # 2. AI manager: get a diagnosis and medicines
        ai_output = self.__ai.get_ai_output(answers_filtered)

        # get_ai_output returns a dictionary when every AI model failed.
        # The key is "error". The value of the key is the message telling
        # patients to seek assistance.
        if "error" in ai_output:
            self.__io.show_message(ai_output["error"])
            return

        # 3. Logic manager: decide and print the route and queue number
        logic_result = self.__logic.process_result(ai_output)

        # 4. Data manager: save the completed record to the database.
        # export_record returns None if saved, or the error message if not.
        export_error = self.__data.export_record(answers, ai_output, logic_result)
        if export_error is not None:
            self.__io.show_message(constants.RECORD_SAVE_FAILED_MESSAGE.format(error=export_error))
        else:
            # 5. I/O manager: tell the patient what to do next
            self.__io.show_result(ai_output, logic_result)
