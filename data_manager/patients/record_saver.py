from data_manager.storage import RecordWriter


class RecordSaver:
    def __init__(
        self, writer: RecordWriter, columns: list[str]
    ):
        self.__writer = writer
        self.__columns = columns

    @staticmethod
    def join_symptoms(patient_record: dict) -> dict:
        """Join the symptoms list into one string, since the database
        column holds text, not a list."""

        symptoms = patient_record.get("current_symptoms")

        if isinstance(symptoms, list):
            patient_record["current_symptoms"] = ", ".join(symptoms)

        return patient_record

    def save(
        self,
        all_user_responses: dict,
        ai_output: dict,
        logic_result: dict
    ) -> str | None:
        # Step 1: Put all the patient information into one dict.
        all_patient_information = {}
        all_patient_information.update(all_user_responses)
        all_patient_information.update(ai_output)
        all_patient_information.update(logic_result)

        # Step 2: Turn the symptoms list into one string,
        all_patient_information = self.join_symptoms(all_patient_information)

        # Step 3: Build the record to save, one entry per column.
        # Only columns in RECORD_COLUMNS are kept, so extra keys like
        # (consent, refused, error) are left out.
        # A missing column is set to None, which the database saves as NULL.
        patient_record = {}
        for column in self.__columns:
            patient_record[column] = all_patient_information.get(column)

        # Step 4: export to cloud Database
        return self.__writer.save(patient_record)
