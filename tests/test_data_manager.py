import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app_test_factory import AppTestFactory
from data_manager import constants
from data_manager.patients import RecordSaver
from data_manager.storage import PostgresRecordWriter
from fakes import FakeDatabase


class TestDataManager:
    # ==========================================================
    # TEST 1 - JOIN SYMPTOMS
    # ==========================================================

    def test_join_symptoms(self):

        fake_patient = {
            "name": "Alex Tan",
            "current_symptoms": [
                "COUGH",
                "FEVER",
                "HEADACHE"
            ]
        }

        database = FakeDatabase([])
        writer = PostgresRecordWriter(database, constants.DEFAULT_RECORDS_TABLE)
        saver = RecordSaver(writer, ["name", "current_symptoms"])

        saver.save(fake_patient, {}, {})
        result = database.executed[0][1]

        print("\nSCENARIO: Join Symptoms")
        print("Input:", ["COUGH", "FEVER", "HEADACHE"])
        print("Expected: COUGH, FEVER, HEADACHE")
        print("Actual:", result["current_symptoms"])

        assert result["current_symptoms"] == (
            "COUGH, FEVER, HEADACHE"
        )

    # ==========================================================
    # TEST 2 - RECORD COLUMNS
    # ==========================================================

    def test_record_columns(self):

        data = AppTestFactory.create_data_manager(FakeDatabase([]))

        record_columns = data.get_record_columns()

        print("\nSCENARIO: Record Columns For The All Records Filter")
        print("Expected:", constants.RECORD_COLUMNS)
        print("Actual:", record_columns)

        assert record_columns == constants.RECORD_COLUMNS

    # ==========================================================
    # TEST 3 - FIND EXISTING PATIENT
    # ==========================================================

    def test_get_patient_by_queue(self):

        # The database returns one row, with the columns in the order asked.
        database = FakeDatabase([("Alex Tan", 25)])
        data = AppTestFactory.create_data_manager(database)

        result = data.get_patient_by_queue(
            "D001",
            ["name", "age"],
            "2026-10-14"
        )

        print("\nSCENARIO: Existing Patient")
        print("Queue: D001")
        print("Expected Patient: Alex Tan")
        print("Actual:")
        print(result)

        assert list(result.columns) == ["name", "age"]
        assert result.iloc[0]["name"] == "Alex Tan"
        assert result.iloc[0]["age"] == 25
        assert database.fetched_parameters == [("D001", "2026-10-14")]

    # ==========================================================
    # TEST 4 - PATIENT DOES NOT EXIST
    # ==========================================================

    def test_patient_not_found(self):

        data = AppTestFactory.create_data_manager(FakeDatabase([]))

        result = data.get_patient_by_queue(
            "D999",
            ["name"],
            "2026-10-14"
        )

        print("\nSCENARIO: Patient Does Not Exist")
        print("Queue: D999")
        print("Expected: Empty result")
        print("Actual:")
        print(result)

        assert result.empty

    # ==========================================================
    # TEST 5 - EXPORT PATIENT RECORD
    # ==========================================================

    def test_export_record(self):

        database = FakeDatabase([])
        data = AppTestFactory.create_data_manager(database)

        user_answers = {
            "name": "Charlie Ng",
            "nric": "S8812345C",
            "gender": "M",
            "birthdate": "1988-03-21",
            "age": "38",
            "phone_number": "+65 91234567",
            "pregnancy": None,
            "current_symptoms": [
                "COUGH",
                "FEVER"
            ],
            "symptom_onset_days": "2",
            "chronic_conditions": "N",
            "current_medications": "N",
            "drug_allergies": "N",
            "consent": "Y"
        }

        ai_output = {
            "primary_diagnosis_ICD11_Code": "CA00",
            "primary_diagnosis_ICD11_Title": "Common Cold",
            "primary_diagnosis_explanation": "Cold symptoms",
            "primary_diagnosis_medicine_1": "PARACETAMOL",
            "primary_diagnosis_medicine_2": None,
            "secondary_diagnosis_ICD11_Code": None,
            "secondary_diagnosis_ICD11_Title": None,
            "secondary_diagnosis_explanation": None,
            "secondary_diagnosis_medicine_1": None,
            "secondary_diagnosis_medicine_2": None,
            "ai_confidence_score": 90
        }

        logic_result = {
            "date": "2026-10-14",
            "time": "12:00",
            "queue_number": "D001",
            "route": "Doctor"
        }

        result = data.export_record(
            user_answers,
            ai_output,
            logic_result
        )

        executed = database.executed
        saved_record = executed[0][1]

        print("\nSCENARIO: Export Patient Record")
        print("Expected Saved Patient: Charlie Ng")
        print("Expected Queue: D001")
        print("Expected Symptoms: COUGH, FEVER")
        print("Actual:")
        print(saved_record)

        assert result is None
        assert len(executed) == 1
        assert 'INSERT INTO "patient_records"' in executed[0][0].as_string()
        assert saved_record["name"] == "Charlie Ng"
        assert saved_record["birthdate"] == "1988-03-21"
        assert saved_record["queue_number"] == "D001"
        assert saved_record["current_symptoms"] == "COUGH, FEVER"
        # Only record columns are saved, so extra keys like consent are left out.
        assert list(saved_record) == constants.RECORD_COLUMNS

    # ==========================================================
    # TEST 6 - ALL PATIENTS ON A DATE
    # ==========================================================

    def test_get_patients_by_date(self):

        # The database returns one row per patient, columns in the order asked.
        database = FakeDatabase([
            ("09:00:00", "D001", "Alex Tan"),
            ("09:30:00", "P001", "Betty Lim")
        ])
        data = AppTestFactory.create_data_manager(database)

        result = data.get_patients_by_date(
            ["name"],
            "2026-10-14"
        )

        print("\nSCENARIO: All Patients On A Date")
        print("Expected Patients: Alex Tan, Betty Lim")
        print("Actual:")
        print(result)

        # Time and queue number are added in front to tell the rows apart.
        assert list(result.columns) == ["time", "queue_number", "name"]
        assert list(result["name"]) == ["Alex Tan", "Betty Lim"]
        assert database.fetched_parameters == [("2026-10-14",)]

    def test_get_patients_by_date_keeps_existing_columns(self):

        data = AppTestFactory.create_data_manager(FakeDatabase([]))

        result = data.get_patients_by_date(
            constants.RECORD_COLUMNS,
            "2026-10-14"
        )

        print("\nSCENARIO: All Records Filter, No Patients")
        print("Expected: Empty result with no repeated columns")
        print("Actual:", list(result.columns)[:4], "...")

        # RECORD_COLUMNS already has time and queue_number, so nothing is added.
        assert list(result.columns) == constants.RECORD_COLUMNS
        assert result.empty
