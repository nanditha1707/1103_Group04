from app import constants
from app.interfaces import DiagnosisSource, PatientRouter, RecordExporter, RegistrationScreens, UserPrompt
from io_manager.patient_answers import Answer


class TriagePipeline:

    def __init__(
        self, screens: RegistrationScreens, prompt: UserPrompt, diagnoser: DiagnosisSource, router: PatientRouter, records: RecordExporter
    ) -> None:
        self.__screens = screens
        self.__prompt = prompt
        self.__diagnoser = diagnoser
        self.__router = router
        self.__records = records

    def process(self, answers: dict[str, Answer]) -> None:
        # Filter answers so only non-personal information goes to the AI.
        answers_filtered = self.__screens.filter_for_ai(answers)

        # 2. AI manager: get a diagnosis and medicines
        ai_output = self.__diagnoser.get_ai_output(answers_filtered)

        # get_ai_output returns a dictionary when every AI model failed.
        # The key is "error". The value of the key is the message telling
        # patients to seek assistance.
        if "error" in ai_output:
            self.__prompt.show_message(ai_output["error"])
            return

        # 3. Logic manager: decide and print the route and queue number
        logic_result = self.__router.process_result(ai_output)

        # 4. Data manager: save the completed record to the database.
        # export_record returns None if saved, or the error message if not.
        export_error = self.__records.export_record(answers, ai_output, logic_result)
        if export_error is not None:
            self.__prompt.show_message(constants.RECORD_SAVE_FAILED_MESSAGE.format(error=export_error))
        else:
            # 5. I/O manager: tell the patient what to do next
            self.__screens.show_result(ai_output, logic_result)
