import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import data_manager as data


def fake_database(monkeypatch, rows):
    """Replace the database with one that always returns rows.
    Returns a list that records the parameters of every query, so a
    test can check the right date and medicine were sent."""

    sent_parameters = []

    def fake_fetch_rows(sql_statement, parameters):
        sent_parameters.append(parameters)
        return rows

    monkeypatch.setattr(
        data,
        "fetch_rows",
        fake_fetch_rows
    )

    return sent_parameters


def test_medicine_count(monkeypatch):

    # COUNT(*) returns one row with one value.
    sent_parameters = fake_database(monkeypatch, [(2,)])

    result = data.get_medicine_count(
        "PARACETAMOL",
        "2026-10-14"
    )

    print("\nSCENARIO: Specific Medicine Count")
    print("Medicine: PARACETAMOL")
    print("Expected: {'PARACETAMOL': 2}")
    print("Actual:", result)

    assert result == {"PARACETAMOL": 2}
    assert sent_parameters == [("2026-10-14", "PARACETAMOL")]


def test_medicine_not_issued(monkeypatch):

    fake_database(monkeypatch, [(0,)])

    result = data.get_medicine_count(
        "IBUPROFEN",
        "2026-10-14"
    )

    print("\nSCENARIO: Medicine Not Issued")
    print("Expected: {}")
    print("Actual:", result)

    assert result == {}


def test_medicine_breakdown(monkeypatch):

    sent_parameters = fake_database(monkeypatch, [
        ("PARACETAMOL", 2),
        ("CETIRIZINE", 1),
        ("IBUPROFEN", 1)
    ])

    result = data.get_medicine_breakdown(
        "2026-10-14"
    )

    print("\nSCENARIO: Medicine Breakdown")
    print("Expected:")
    print("PARACETAMOL = 2")
    print("IBUPROFEN = 1")
    print("CETIRIZINE = 1")
    print("Actual:")
    print(result)

    assert result["PARACETAMOL"] == 2
    assert result["IBUPROFEN"] == 1
    assert result["CETIRIZINE"] == 1
    assert sent_parameters == [("2026-10-14",)]


def test_patient_type_breakdown(monkeypatch):

    fake_database(monkeypatch, [
        ("Retail", 1),
        ("Doctor", 1),
        ("Pharmacist", 1)
    ])

    result = data.get_patient_type_breakdown(
        "2026-10-14"
    )

    print("\nSCENARIO: Patient Type Breakdown")
    print("Expected:")
    print("Doctor = 1")
    print("Pharmacy = 1")
    print("Retail = 1")
    print("Actual:")
    print(result)

    # Labels follow the order of ROUTE_LABELS, not the database order.
    assert list(result) == ["Doctor", "Pharmacy", "Retail"]
    assert result["Doctor"] == 1
    assert result["Pharmacy"] == 1
    assert result["Retail"] == 1


def test_reports_database_down(monkeypatch):

    fake_database(monkeypatch, None)

    print("\nSCENARIO: Database Cannot Be Reached")
    print("Expected: None from every report")

    assert data.get_medicine_count("PARACETAMOL", "2026-10-14") is None
    assert data.get_medicine_breakdown("2026-10-14") is None
    assert data.get_patient_type_breakdown("2026-10-14") is None
