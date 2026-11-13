import sys
from datetime import date, datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fakes import FakeConsole
from io_manager import IOManager, constants
from io_manager.form import RegistrationFactory

CONFIRM_ALL_INPUTS = "17"
MINIMUM_AGE = RegistrationFactory.MINIMUM_SELF_REGISTRATION_AGE


def birthdate_for_age(age):

    today = datetime.now(RegistrationFactory.TIMEZONE).date()

    return date(today.year - age, 1, 1).isoformat()


def register(answers):

    console = FakeConsole(answers)
    io = IOManager(console, symptom_terms=["SORE THROAT"])

    return io.collect_registration(), console


def test_normal_female_registration():

    # Automatically answers every registration question.
    result, console = register([
        "Y",                    # Consent
        "NANI",                 # Name
        "T0111111C",            # NRIC
        "F",                    # Gender
        birthdate_for_age(20),  # Birthdate
        "+65 91111111",         # Phone
        "N",                    # Pregnant
        "N",                    # Chest pain
        "N",                    # Breathing difficulties
        "N",                    # Signs of stroke
        "N",                    # Self-harm
        "1",                    # Symptom: Cough
        "7",                    # Done adding symptoms
        "2",                    # Symptoms started 2 days ago
        "N",                    # Chronic conditions
        "N",                    # Current medication
        "N",                    # Drug allergies
        CONFIRM_ALL_INPUTS
    ])

    print("\nSCENARIO: Normal Female Registration")
    print("Expected: Registration completes")
    print("Expected Gender: F")
    print("Expected Age: 20")
    print("Expected Pregnancy: N")
    print("Expected Symptoms: ['COUGH']")
    print("Actual:")
    print(result)

    assert result is not None
    assert result["name"] == "NANI"
    assert result["gender"] == "F"
    assert result["birthdate"] == birthdate_for_age(20)
    assert result["age"] == "20"
    assert result["pregnancy"] == "N"
    assert result["current_symptoms"] == ["COUGH"]
    assert console.shown[-1] == constants.CONFIRMED_MESSAGE


def test_normal_male_registration():

    # The program should automatically skip pregnancy for males.
    result, console = register([
        "Y",
        "ALEX TAN",
        "S0012345B",
        "M",
        birthdate_for_age(25),
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
        "N",
        CONFIRM_ALL_INPUTS
    ])

    print("\nSCENARIO: Normal Male Registration")
    print("Expected: Pregnancy question skipped")
    print("Expected Pregnancy Value: None")
    print("Actual:")
    print(result)

    assert result is not None
    assert result["gender"] == "M"
    assert result["pregnancy"] is None
    assert result["current_symptoms"] == ["FLU"]
    assert constants.PREGNANCY_PROMPT not in console.prompts


def test_no_consent():

    result, console = register([
        "N"
    ])

    print("\nSCENARIO: Patient Does Not Consent")
    print("Expected: Registration stops")
    print("Actual:", result)

    assert result is None
    assert console.shown[-1] == constants.REG_EXIT_MESSAGE


def test_emergency_chest_pain():

    result, console = register([
        "Y",
        "CHARLIE NG",
        "S8812345C",
        "M",
        birthdate_for_age(58),
        "+65 92345678",

        # Pregnancy skipped.

        "Y"                 # Chest pain
    ])

    print("\nSCENARIO: Emergency Chest Pain")
    print("Chest Pain: Y")
    print("Expected: Registration stops and patient is sent to nurse")
    print("Actual:", result)

    assert result is None
    assert console.shown[-1] == constants.NURSE_ALERT_MESSAGE


def test_underage_patient():

    result, console = register([
        "Y",
        "JANE TAN",
        "T1111111A",
        "F",
        birthdate_for_age(MINIMUM_AGE - 1)      # Birthdate
    ])

    print("\nSCENARIO: Underage Patient")
    print("Age:", MINIMUM_AGE - 1)
    print("Expected: Registration stops and patient is sent to manual registration")
    print("Actual:", result)

    assert result is None
    assert console.shown[-1] == constants.UNDERAGE_MESSAGE.format(minimum=MINIMUM_AGE)
