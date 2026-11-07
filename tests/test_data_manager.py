import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

import data_manager as data


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

    result = data.clean_icd_data(fake_icd)

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

    result = data.clean_hsa_data(fake_hsa)

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

    result = data.join_symptoms(fake_patient)

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

    patient_filter = data.get_patient_filter("1")
    medical_filter = data.get_patient_filter("2")
    ai_filter = data.get_patient_filter("3")
    all_filter = data.get_patient_filter("4")

    print("\nSCENARIO: Patient Filters")
    print("Option 1:", patient_filter)
    print("Option 2:", medical_filter)
    print("Option 3:", ai_filter)
    print("Option 4:", all_filter)

    assert patient_filter == data.PATIENT_COLUMNS
    assert medical_filter == data.MEDICAL_COLUMNS
    assert ai_filter == data.AI_OUTPUT_COLUMN
    assert all_filter == data.RECORD_COLUMNS




# ==========================================================
# FAKE DATABASE CONNECTION
# ==========================================================
# Stands in for psycopg.connect so the tests never touch the real
# cloud database. It records every statement it is asked to run.

class FakeCursor:

    def __init__(self):
        self.executed = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql_statement, parameters):
        self.executed.append((sql_statement, parameters))

    def fetchall(self):
        return []


class FakeConnection:

    def __init__(self):
        self.fake_cursor = FakeCursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def cursor(self):
        return self.fake_cursor


# ==========================================================
# TEST 5 - FIND EXISTING PATIENT
# ==========================================================

def test_get_patient_by_queue(monkeypatch):

    sent_parameters = []

    # The database returns one row, with the columns in the order asked.
    def fake_fetch_rows(sql_statement, parameters):
        sent_parameters.append(parameters)
        return [("Alex Tan", 25)]

    monkeypatch.setattr(
        data,
        "fetch_rows",
        fake_fetch_rows
    )

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
    assert sent_parameters == [("D001", "2026-10-14")]


# ==========================================================
# TEST 6 - PATIENT DOES NOT EXIST
# ==========================================================

def test_patient_not_found(monkeypatch):

    monkeypatch.setattr(
        data,
        "fetch_rows",
        lambda sql_statement, parameters: []
    )

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

def test_export_record(monkeypatch):

    fake_connection = FakeConnection()

    monkeypatch.setattr(
        data.psycopg,
        "connect",
        lambda url: fake_connection
    )

    user_answers = {
        "name": "Charlie Ng",
        "nric": "S8812345C",
        "gender": "M",
        "age": 38,
        "phone_number": "+65 91234567",
        "pregnancy": None,
        "current_symptoms": [
            "COUGH",
            "FEVER"
        ],
        "symptom_onset_days": 2,
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

    executed = fake_connection.fake_cursor.executed
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
    assert saved_record["queue_number"] == "D001"
    assert saved_record["current_symptoms"] == "COUGH, FEVER"
    # Only record columns are saved, so extra keys like consent are left out.
    assert list(saved_record) == data.RECORD_COLUMNS


# ==========================================================
# TEST 8 - DATABASE CANNOT BE REACHED
# ==========================================================

def test_database_down(monkeypatch):

    def fake_connect(url):
        raise data.psycopg.OperationalError("connection refused")

    monkeypatch.setattr(
        data.psycopg,
        "connect",
        fake_connect
    )

    fetch_result = data.fetch_rows(
        "SELECT 1",
        ()
    )
    export_result = data.export_record(
        {"name": "Charlie Ng"},
        {},
        {"queue_number": "D001"}
    )

    print("\nSCENARIO: Database Cannot Be Reached")
    print("Expected fetch_rows: None")
    print("Expected export_record: an error message")
    print("Actual:", fetch_result, "|", export_result)

    assert fetch_result is None
    assert "connection refused" in export_result
