import sys
from pathlib import Path

import pandas as pd
import psycopg

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import DataManagerFactory, constants
from data_manager.dataset import HsaDataset, IcdDataset
from data_manager.patients import RecordSaver
from data_manager.storage import PostgresDatabase
from fakes import FakeDatabase


# ==========================================================
# TEST 1 - CLEAN ICD DATA
# ==========================================================

def test_clean_icd_data():

    fake_icd = pd.DataFrame({
        "Code": [
            " ca00 ",
            "CA00",
            "8A80",
            "CA02",
            "CA03"
        ],
        "Title": [
            " Acute nasopharyngitis ",
            "Acute nasopharyngitis",
            "Migraine",
            "",
            "-"
        ]
    })

    result = IcdDataset(constants.ICD_CSV_PATH).clean(fake_icd)

    print("\nSCENARIO: Clean ICD Data")
    print("Expected:")
    print("- Codes and names stripped and uppercased")
    print("- Duplicate Acute nasopharyngitis removed")
    print("- Empty value removed")
    print("- Dash value removed")
    print("- Migraine remains")
    print("Actual:")
    print(result)

    assert list(result["Code"]) == [
        "CA00",
        "8A80"
    ]
    assert list(result["DiseaseName"]) == [
        "ACUTE NASOPHARYNGITIS",
        "MIGRAINE"
    ]


# ==========================================================
# TEST 2 - CLEAN HSA DATA
# ==========================================================

def test_clean_hsa_data():

    fake_hsa = pd.DataFrame([
        {
            "Productname": " paracetamol ",
            "Dosageform": "Tablet",
            "Strength": "500mg",
            "Activeingredients": " paracetamol ",
            "ATCCode": "N02BE01",
            "Forensicclassification": "General Sale List"
        },
        {
            "Productname": " paracetamol ",
            "Dosageform": "Tablet",
            "Strength": "500mg",
            "Activeingredients": " paracetamol ",
            "ATCCode": "N02BE01",
            "Forensicclassification": "General Sale List"
        }
    ])

    result = HsaDataset(constants.HSA_CSV_PATH).clean(fake_hsa)

    print("\nSCENARIO: Clean HSA Data")
    print("Expected Drug Name: PARACETAMOL")
    print("Expected Active Ingredient: PARACETAMOL")
    print("Expected Rows: 1")
    print("Actual:")
    print(result)

    assert len(result) == 1
    assert result.iloc[0]["DrugName"] == "PARACETAMOL"
    assert result.iloc[0]["ActiveIngredients"] == "PARACETAMOL"


# ==========================================================
# TEST 3 - JOIN SYMPTOMS
# ==========================================================

def test_join_symptoms():

    fake_patient = {
        "name": "Alex Tan",
        "current_symptoms": [
            "COUGH",
            "FEVER",
            "HEADACHE"
        ]
    }

    result = RecordSaver.join_symptoms(fake_patient)

    print("\nSCENARIO: Join Symptoms")
    print("Input:", ["COUGH", "FEVER", "HEADACHE"])
    print("Expected: COUGH, FEVER, HEADACHE")
    print("Actual:", result["current_symptoms"])

    assert result["current_symptoms"] == (
        "COUGH, FEVER, HEADACHE"
    )


# ==========================================================
# TEST 4 - PATIENT FILTER OPTIONS
# ==========================================================

def test_patient_filters():

    data = DataManagerFactory.create(FakeDatabase([]))

    patient_filter = data.get_patient_filter("1")
    medical_filter = data.get_patient_filter("2")
    ai_filter = data.get_patient_filter("3")
    all_filter = data.get_patient_filter("4")

    print("\nSCENARIO: Patient Filters")
    print("Option 1:", patient_filter)
    print("Option 2:", medical_filter)
    print("Option 3:", ai_filter)
    print("Option 4:", all_filter)

    assert patient_filter == constants.PATIENT_COLUMNS
    assert medical_filter == constants.MEDICAL_COLUMNS
    assert ai_filter == constants.AI_OUTPUT_COLUMNS
    assert all_filter == constants.RECORD_COLUMNS


# ==========================================================
# TEST 5 - FIND EXISTING PATIENT
# ==========================================================

def test_get_patient_by_queue():

    # The database returns one row, with the columns in the order asked.
    database = FakeDatabase([("Alex Tan", 25)])
    data = DataManagerFactory.create(database)

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
# TEST 6 - PATIENT DOES NOT EXIST
# ==========================================================

def test_patient_not_found():

    data = DataManagerFactory.create(FakeDatabase([]))

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
# TEST 7 - EXPORT PATIENT RECORD
# ==========================================================

def test_export_record():

    database = FakeDatabase([])
    data = DataManagerFactory.create(database)

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
    assert "INSERT INTO patient_records" in executed[0][0]
    assert saved_record["name"] == "Charlie Ng"
    assert saved_record["birthdate"] == "1988-03-21"
    assert saved_record["queue_number"] == "D001"
    assert saved_record["current_symptoms"] == "COUGH, FEVER"
    # Only record columns are saved, so extra keys like consent are left out.
    assert list(saved_record) == constants.RECORD_COLUMNS


# ==========================================================
# TEST 8 - DATABASE CANNOT BE REACHED
# ==========================================================

def test_database_down(monkeypatch):

    def fake_connect(url):
        raise psycopg.OperationalError("connection refused")

    monkeypatch.setattr(
        psycopg,
        "connect",
        fake_connect
    )

    database = PostgresDatabase("postgresql://unreachable")
    data = DataManagerFactory.create(database)

    fetch_result = database.fetch_rows(
        "SELECT 1",
        ()
    )
    query_result = data.get_patient_by_queue(
        "D001",
        ["name"],
        "2026-10-14"
    )
    export_result = data.export_record(
        {"name": "Charlie Ng"},
        {},
        {"queue_number": "D001"}
    )

    print("\nSCENARIO: Database Cannot Be Reached")
    print("Expected fetch_rows: None")
    print("Expected get_patient_by_queue: None")
    print("Expected export_record: an error message")
    print("Actual:", fetch_result, "|", query_result, "|", export_result)

    assert fetch_result is None
    assert query_result is None
    assert "connection refused" in export_result


# ==========================================================
# TEST 9 - ALL PATIENTS ON A DATE
# ==========================================================

def test_get_patients_by_date():

    # The database returns one row per patient, columns in the order asked.
    database = FakeDatabase([
        ("09:00:00", "D001", "Alex Tan"),
        ("09:30:00", "P001", "Betty Lim")
    ])
    data = DataManagerFactory.create(database)

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


def test_get_patients_by_date_keeps_existing_columns():

    data = DataManagerFactory.create(FakeDatabase([]))

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
