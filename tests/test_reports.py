import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

import data_manager as data


def setup_records(tmp_path, monkeypatch):

    records = pd.DataFrame([
        {
            "date": "2026-10-14",
            "route": "Doctor",
            "primary_diagnosis_medicine_1": "PARACETAMOL",
            "primary_diagnosis_medicine_2": None,
            "secondary_diagnosis_medicine_1": None,
            "secondary_diagnosis_medicine_2": None
        },
        {
            "date": "2026-10-14",
            "route": "Pharmacist",
            "primary_diagnosis_medicine_1": "PARACETAMOL",
            "primary_diagnosis_medicine_2": "IBUPROFEN",
            "secondary_diagnosis_medicine_1": None,
            "secondary_diagnosis_medicine_2": None
        },
        {
            "date": "2026-10-14",
            "route": "Retail",
            "primary_diagnosis_medicine_1": "CETIRIZINE",
            "primary_diagnosis_medicine_2": None,
            "secondary_diagnosis_medicine_1": None,
            "secondary_diagnosis_medicine_2": None
        }
    ])

    test_file = tmp_path / "patient_records.csv"
    records.to_csv(test_file, index=False)

    monkeypatch.setattr(
        data,
        "RECORDS_CSV_PATH",
        test_file
    )


def test_medicine_count(tmp_path, monkeypatch):
    setup_records(tmp_path, monkeypatch)

    result = data.get_medicine_count(
        "2026-10-14",
        "PARACETAMOL"
    )

    print("\nMedicine Count:")
    print(result)

    assert result == 2


def test_medicine_breakdown(tmp_path, monkeypatch):
    setup_records(tmp_path, monkeypatch)

    result = data.get_medicine_breakdown(
        "2026-10-14"
    )

    print("\nMedicine Breakdown:")
    print(result)

    assert result["PARACETAMOL"] == 2
    assert result["IBUPROFEN"] == 1
    assert result["CETIRIZINE"] == 1


def test_patient_type_breakdown(tmp_path, monkeypatch):
    setup_records(tmp_path, monkeypatch)

    result = data.get_patient_type_breakdown(
        "2026-10-14"
    )

    print("\nPatient Type Breakdown:")
    print(result)

    assert result["Doctor"] == 1
    assert result["Pharmacy"] == 1
    assert result["Retail"] == 1