import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import io_manager as io


def give_inputs(monkeypatch, answers):
    fake_inputs = iter(answers)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(fake_inputs)
    )


def test_normal_female_registration(monkeypatch):

    # Automatically answers every registration question.
    give_inputs(monkeypatch, [
        "Y",                # Consent
        "NANI",             # Name
        "T0111111C",        # NRIC
        "F",                # Gender
        "20",               # Age
        "+65 91111111",     # Phone
        "N",                # Pregnant
        "N",                # Chest pain
        "N",                # Breathing difficulties
        "N",                # Signs of stroke
        "N",                # Self-harm
        "1",                # Symptom: Cough
        "7",                # Done adding symptoms
        "2",                # Symptoms started 2 days ago
        "N",                # Chronic conditions
        "N",                # Current medication
        "N"                 # Drug allergies
    ])

    result = io.run_questions()

    print("\nSCENARIO: Normal Female Registration")
    print("Expected: Registration completes")
    print("Expected Gender: F")
    print("Expected Pregnancy: N")
    print("Expected Symptoms: ['COUGH']")
    print("Actual:")
    print(result)

    assert result is not None
    assert result["name"] == "NANI"
    assert result["gender"] == "F"
    assert result["pregnancy"] == "N"
    assert result["current_symptoms"] == ["COUGH"]


def test_normal_male_registration(monkeypatch):

    # The program should automatically skip pregnancy for males.
    give_inputs(monkeypatch, [
        "Y",
        "ALEX TAN",
        "S0012345B",
        "M",
        "25",
        "+65 91234567",
        # Pregnancy is skipped here.
        "N",                # Chest pain
        "N",                # Breathing difficulties
        "N",                # Signs of stroke
        "N",                # Self-harm
        "2",                # Flu
        "7",                # Done
        "3",                # 3 days
        "N",
        "N",
        "N"
    ])

    result = io.run_questions()

    print("\nSCENARIO: Normal Male Registration")
    print("Expected: Pregnancy question skipped")
    print("Expected Pregnancy Value: None")
    print("Actual:")
    print(result)

    assert result is not None
    assert result["gender"] == "M"
    assert result["pregnancy"] is None
    assert result["current_symptoms"] == ["FLU"]


def test_no_consent(monkeypatch):

    give_inputs(monkeypatch, [
        "N"
    ])

    result = io.run_questions()

    print("\nSCENARIO: Patient Does Not Consent")
    print("Expected: Registration stops")
    print("Actual:", result)

    assert result is None


def test_emergency_chest_pain(monkeypatch):

    give_inputs(monkeypatch, [
        "Y",
        "CHARLIE NG",
        "S8812345C",
        "M",
        "58",
        "+65 92345678",

        # Pregnancy skipped.

        "Y"                 # Chest pain
    ])

    result = io.run_questions()

    print("\nSCENARIO: Emergency Chest Pain")
    print("Chest Pain: Y")
    print("Expected: Registration stops and patient is sent to nurse")
    print("Actual:", result)

    assert result is None


def test_underage_patient(monkeypatch):

    give_inputs(monkeypatch, [
        "Y",
        "JANE TAN",
        "T1111111A",
        "F",
        "17"                # Age
    ])

    result = io.run_questions()

    print("\nSCENARIO: Underage Patient")
    print("Age: 17")
    print("Expected: Registration stops and patient is sent to manual registration")
    print("Actual:", result)

    assert result is None