import sys
from pathlib import Path

# Allow imports from the main project folder
sys.path.append(
    str(Path(__file__).parent.parent)
)

from logic_manager import (
    get_medicines,
    get_classification,
    process_result
)

from validation_data import get_cleaned_datasets

# Load cleaned datasets
icd_df, hsa_df = get_cleaned_datasets()


# Sample AI output
ai_output = {
    "primary_diagnosis_ICD11_Title":
        "Influenza due to identified influenza virus",

    "primary_diagnosis_ICD11_Code":
        "1C80.0",

    "secondary_diagnosis_ICD11_Title":
        "Acute upper respiratory infection",

    "secondary_diagnosis_ICD11_Code":
        "CA00",

    "primary_diagnosis_medicine_1":
        "Oseltamivir",

    "primary_diagnosis_medicine_2":
        "Paracetamol",

    "secondary_diagnosis_medicine_1":
        "Dextromethorphan",

    "secondary_diagnosis_medicine_2":
        "Chlorpheniramine",

    "ai_confidence_score": 85,
    "refused": "false"
}


# Test AI bypass route
all_user_responses = {
    "ai_bypass": True
}


# Get medicines from AI output
medicines = get_medicines(ai_output)

print("\nMEDICATION CLASSIFICATIONS")
print("--------------------------")

# Check each medicine's classification
for medicine in medicines:
    classification = get_classification(
        medicine,
        hsa_df
    )

    print(
        medicine,
        "->",
        classification
    )


# Process final routing result
result = process_result(
    all_user_responses,
    ai_output,
    hsa_df
)

print("\nFINAL RESULT")
print("------------")
print(result)