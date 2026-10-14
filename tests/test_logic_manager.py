import sys
from pathlib import Path

import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
    )

import logic_manager as logic


def make_hsa_data():

    return pd.DataFrame([
        {
            "DrugName": "AMOXICILLIN",
            "ActiveIngredients": "AMOXICILLIN",
            "Classification": "Prescription Only"
        },
        {
            "DrugName": "CHLORPHENIRAMINE",
            "ActiveIngredients": "CHLORPHENIRAMINE",
            "Classification": "Pharmacy Only"
        },
        {
            "DrugName": "PARACETAMOL",
            "ActiveIngredients": "PARACETAMOL",
            "Classification": "General Sale List"
        }
    ])


def base_ai_output():

    return {
        "primary_diagnosis_explanation": "",
        "secondary_diagnosis_explanation": "",
        "primary_diagnosis_medicine_1": "",
        "primary_diagnosis_medicine_2": "",
        "secondary_diagnosis_medicine_1": "",
        "secondary_diagnosis_medicine_2": ""
    }


def test_emergency_route():

    ai_output = base_ai_output()

    ai_output["primary_diagnosis_explanation"] = (
        "This may be an EMERGENCY."
    )

    result = logic.decide_route(
        ai_output,
        make_hsa_data()
    )

    print("\nSCENARIO: Emergency")
    print("Expected: EMERGENCY")
    print("Actual:", result)

    assert result == "EMERGENCY"


def test_doctor_route():

    ai_output = base_ai_output()

    ai_output["primary_diagnosis_medicine_1"] = (
        "AMOXICILLIN"
    )

    result = logic.decide_route(
        ai_output,
        make_hsa_data()
    )

    print("\nSCENARIO: Prescription Medicine")
    print("Medicine: AMOXICILLIN")
    print("Expected: Doctor")
    print("Actual:", result)

    assert result == "Doctor"


def test_pharmacist_route():

    ai_output = base_ai_output()

    ai_output["primary_diagnosis_medicine_1"] = (
        "CHLORPHENIRAMINE"
    )

    result = logic.decide_route(
        ai_output,
        make_hsa_data()
    )

    print("\nSCENARIO: Pharmacy Only Medicine")
    print("Medicine: CHLORPHENIRAMINE")
    print("Expected: Pharmacist")
    print("Actual:", result)

    assert result == "Pharmacist"


def test_retail_route():

    ai_output = base_ai_output()

    ai_output["primary_diagnosis_medicine_1"] = (
        "PARACETAMOL"
    )

    result = logic.decide_route(
        ai_output,
        make_hsa_data()
    )

    print("\nSCENARIO: General Sale Medicine")
    print("Medicine: PARACETAMOL")
    print("Expected: Retail")
    print("Actual:", result)

    assert result == "Retail"