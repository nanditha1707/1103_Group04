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
        "Title": [
            "Common Cold",
            "Common Cold",
            "Migraine",
            "",
            "-"
        ]
    })

    result = data.clean_icd_data(fake_icd)

    print("\nSCENARIO: Clean ICD Data")
    print("Expected:")
    print("- Duplicate Common Cold removed")
    print("- Empty value removed")
    print("- Dash value removed")
    print("- Migraine remains")
    print("Actual:")
    print(result)

    assert list(result["DiseaseName"]) == [
        "Common Cold",
        "Migraine"
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
# TEST 5 - FIND EXISTING PATIENT
# ==========================================================

def test_get_patient_by_queue():

    fake_records = pd.DataFrame([
        {
            "date": "2026-10-14",
            "queue_number": "D001",
            "name": "Alex Tan",
            "age": 25
        },
        {
            "date": "2026-10-14",
            "queue_number": "P001",
            "name": "Betty Lim",
            "age": 30
        }
    ])

    result = data.get_patient_by_queue(
        fake_records,
        "D001",
        ["name", "age"],
        "2026-10-14"
    )

    print("\nSCENARIO: Existing Patient")
    print("Queue: D001")
    print("Expected Patient: Alex Tan")
    print("Actual:")
    print(result)

    assert not result.empty
    assert result.iloc[0]["name"] == "Alex Tan"
    assert result.iloc[0]["age"] == 25


# ==========================================================
# TEST 6 - PATIENT DOES NOT EXIST
# ==========================================================

def test_patient_not_found():

    fake_records = pd.DataFrame([
        {
            "date": "2026-10-14",
            "queue_number": "D001",
            "name": "Alex Tan"
        }
    ])

    result = data.get_patient_by_queue(
        fake_records,
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

def test_export_record(tmp_path, monkeypatch):

    test_records_path = (
        tmp_path / "patient_records.csv"
    )

    test_records_dir = tmp_path

    monkeypatch.setattr(
        data,
        "RECORDS_CSV_PATH",
        test_records_path
    )

    monkeypatch.setattr(
        data,
        "RECORDS_DIR",
        test_records_dir
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
        "drug_allergies": "N"
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
        logic_result,
        None
    )

    saved_records = pd.read_csv(
        test_records_path
    )

    print("\nSCENARIO: Export Patient Record")
    print("Expected Saved Patient: Charlie Ng")
    print("Expected Queue: D001")
    print("Expected Symptoms: COUGH, FEVER")
    print("Actual:")
    print(saved_records)

    assert result is True
    assert len(saved_records) == 1
    assert saved_records.iloc[0]["name"] == "Charlie Ng"
    assert saved_records.iloc[0]["queue_number"] == "D001"
    assert saved_records.iloc[0]["current_symptoms"] == (
        "COUGH, FEVER"
    )


# ==========================================================
# TEST 8 - LOAD PATIENT RECORDS
# ==========================================================

def test_load_records(tmp_path, monkeypatch):

    test_file = tmp_path / "patient_records.csv"

    fake_records = pd.DataFrame([
        {
            "date": "2026-10-14",
            "queue_number": "D001",
            "name": "Alex Tan"
        },
        {
            "date": "2026-10-14",
            "queue_number": "P001",
            "name": "Betty Lim"
        }
    ])

    fake_records.to_csv(
        test_file,
        index=False
    )

    monkeypatch.setattr(
        data,
        "RECORDS_CSV_PATH",
        test_file
    )

    result = data.load_records()

    print("\nSCENARIO: Load Patient Records")
    print("Expected Records: 2")
    print("Actual Records:", len(result))
    print(result)

    assert len(result) == 2
    assert result.iloc[0]["name"] == "Alex Tan"
    assert result.iloc[1]["name"] == "Betty Lim"