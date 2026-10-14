import sys
from pathlib import Path

import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
    )

import logic_manager as logic


# ==========================================================
# FAKE HSA DATA
# ==========================================================
# This replaces the need to use live external data during testing.

def get_fake_hsa_data():

    return pd.DataFrame([
        {
            "DrugName": "PARACETAMOL",
            "ActiveIngredients": "PARACETAMOL",
            "Classification": "General Sale List"
        },
        {
            "DrugName": "CETIRIZINE",
            "ActiveIngredients": "CETIRIZINE",
            "Classification": "General Sale List"
        },
        {
            "DrugName": "IBUPROFEN",
            "ActiveIngredients": "IBUPROFEN",
            "Classification": "General Sale List"
        },
        {
            "DrugName": "LOZENGES",
            "ActiveIngredients": "LOZENGES",
            "Classification": "General Sale List"
        },
        {
            "DrugName": "CHLORPHENIRAMINE",
            "ActiveIngredients": "CHLORPHENIRAMINE",
            "Classification": "Pharmacy Only"
        },
        {
            "DrugName": "AMOXICILLIN",
            "ActiveIngredients": "AMOXICILLIN",
            "Classification": "Prescription Only"
        }
    ])


# ==========================================================
# CASE 1 - ALL 4 MEDICINES ARE RETAIL
# ==========================================================

def test_all_retail_medicines():

    # Hardcoded sample AI response.
    ai_output = {
        "primary_diagnosis_explanation":
            "Patient has mild cold symptoms.",

        "secondary_diagnosis_explanation":
            "No emergency symptoms detected.",

        "primary_diagnosis_medicine_1":
            "PARACETAMOL",

        "primary_diagnosis_medicine_2":
            "CETIRIZINE",

        "secondary_diagnosis_medicine_1":
            "IBUPROFEN",

        "secondary_diagnosis_medicine_2":
            "LOZENGES"
    }

    result = logic.decide_route(
        ai_output,
        get_fake_hsa_data()
    )

    print("\nCASE 1: ALL RETAIL MEDICINES")
    print("PARACETAMOL -> Retail")
    print("CETIRIZINE -> Retail")
    print("IBUPROFEN -> Retail")
    print("LOZENGES -> Retail")
    print("Expected Route: Retail")
    print("Actual Route:", result)

    assert result == "Retail"


# ==========================================================
# CASE 2 - 3 RETAIL + 1 PHARMACY ONLY
# ==========================================================

def test_pharmacy_medicine_overrides_retail():

    # Hardcoded sample AI response.
    ai_output = {
        "primary_diagnosis_explanation":
            "Patient has flu-like symptoms.",

        "secondary_diagnosis_explanation":
            "No emergency symptoms detected.",

        "primary_diagnosis_medicine_1":
            "PARACETAMOL",

        "primary_diagnosis_medicine_2":
            "CETIRIZINE",

        "secondary_diagnosis_medicine_1":
            "IBUPROFEN",

        "secondary_diagnosis_medicine_2":
            "CHLORPHENIRAMINE"
    }

    result = logic.decide_route(
        ai_output,
        get_fake_hsa_data()
    )

    print("\nCASE 2: 3 RETAIL + 1 PHARMACY")
    print("PARACETAMOL -> Retail")
    print("CETIRIZINE -> Retail")
    print("IBUPROFEN -> Retail")
    print("CHLORPHENIRAMINE -> Pharmacy Only")
    print("Expected Route: Pharmacist")
    print("Actual Route:", result)

    assert result == "Pharmacist"


# ==========================================================
# CASE 3 - PRESCRIPTION MEDICINE OVERRIDES PHARMACY/RETAIL
# ==========================================================

def test_prescription_medicine_overrides_other_routes():

    # Hardcoded sample AI response.
    ai_output = {
        "primary_diagnosis_explanation":
            "Patient may have a bacterial infection.",

        "secondary_diagnosis_explanation":
            "No emergency symptoms detected.",

        "primary_diagnosis_medicine_1":
            "PARACETAMOL",

        "primary_diagnosis_medicine_2":
            "CHLORPHENIRAMINE",

        "secondary_diagnosis_medicine_1":
            "AMOXICILLIN",

        "secondary_diagnosis_medicine_2":
            "CETIRIZINE"
    }

    result = logic.decide_route(
        ai_output,
        get_fake_hsa_data()
    )

    print("\nCASE 3: PRESCRIPTION MEDICINE PRESENT")
    print("PARACETAMOL -> Retail")
    print("CHLORPHENIRAMINE -> Pharmacy Only")
    print("AMOXICILLIN -> Prescription Only")
    print("CETIRIZINE -> Retail")
    print("Expected Route: Doctor")
    print("Actual Route:", result)

    assert result == "Doctor"


# ==========================================================
# CASE 4 - EMERGENCY OVERRIDES ALL MEDICINES
# ==========================================================

def test_emergency_overrides_medicine_routing():

    # Hardcoded sample AI response.
    ai_output = {
        "primary_diagnosis_explanation":
            "EMERGENCY: Patient requires immediate medical attention.",

        "secondary_diagnosis_explanation":
            "Urgent assessment is required.",

        "primary_diagnosis_medicine_1":
            "PARACETAMOL",

        "primary_diagnosis_medicine_2":
            "CETIRIZINE",

        "secondary_diagnosis_medicine_1":
            "IBUPROFEN",

        "secondary_diagnosis_medicine_2":
            "LOZENGES"
    }

    result = logic.decide_route(
        ai_output,
        get_fake_hsa_data()
    )

    print("\nCASE 4: EMERGENCY")
    print("All medicines are Retail.")
    print("AI explanation contains EMERGENCY.")
    print("Expected Route: EMERGENCY")
    print("Actual Route:", result)

    assert result == "EMERGENCY"