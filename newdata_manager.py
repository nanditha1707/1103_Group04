# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
from pathlib import Path
import shutil
 
import pandas as pd
from dataset import Dataset
from hsa_dataset import HsaDataset
from icd_dataset import IcdDataset
from patient_record import PatientRecord

# Folder paths, based on where this file is, not where the program is run from.
# Every module gets its file paths from here.
PROJECT_DIR = Path(__file__).resolve().parent
# Read-only datasets that ship with the app.
DATASETS_DIR = PROJECT_DIR / "datasets"
# Saved patient records.
RECORDS_DIR = PROJECT_DIR / "records"
# Exported query results.
QUERY_DIR = PROJECT_DIR / "query"

# File paths.
ICD_CSV_PATH = DATASETS_DIR / "icd11.csv"
HSA_CSV_PATH = DATASETS_DIR / "hsa.csv"
SYMPTOMS_CSV_PATH = DATASETS_DIR / "symptoms_umls.csv"

# CSV file used to store patient records.
# Same file logic_manager reads to work out queue numbers.
RECORDS_CSV_PATH = RECORDS_DIR / "patient_records.csv"

# Starter patient records, copied to RECORDS_CSV_PATH on the first run.
SEED_RECORDS_CSV_PATH = DATASETS_DIR / "patient_records_seed.csv"

# Fixed column order for patient_records.csv.
# Every row uses this same list, so a failed AI response (which only
# has an "error" key) leaves its columns blank instead of shifting them.
RECORD_COLUMNS = [
    "date",
    "time",
    "queue_number",
    "name", 
    "nric", 
    "gender", 
    "age", 
    "phone_number",
    "pregnancy",
    "current_symptoms",
    "symptom_onset_days",
    "chronic_conditions",
    "current_medications",
    "drug_allergies",
    "primary_diagnosis_ICD11_Code",
    "primary_diagnosis_ICD11_Title",
    "primary_diagnosis_explanation",
    "primary_diagnosis_medicine_1",
    "primary_diagnosis_medicine_2",
    "secondary_diagnosis_ICD11_Code",
    "secondary_diagnosis_ICD11_Title",
    "secondary_diagnosis_explanation",
    "secondary_diagnosis_medicine_1",
    "secondary_diagnosis_medicine_2",
    "ai_confidence_score",
    "route"
]
# Column groups shown by each healthcare portal query filter option.
PATIENT_COLUMNS=[
    "name", 
    "nric", 
    "gender", 
    "age", 
    "phone_number"
                 ]
MEDICAL_COLUMNS=[
    "date",
    "route",
    "pregnancy",
    "current_symptoms",
    "symptom_onset_days",
    "chronic_conditions",
    "current_medications",
    "drug_allergies",
        ]

AI_OUTPUT_COLUMN=[
        "primary_diagnosis_ICD11_Code",
        "primary_diagnosis_ICD11_Title",
        "primary_diagnosis_explanation",
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_ICD11_Code",
        "secondary_diagnosis_ICD11_Title",
        "secondary_diagnosis_explanation",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2",
        "ai_confidence_score"
            ]
# Medicine fields from AI output.
MEDICINE_FIELDS=[
    "primary_diagnosis_medicine_1",
    "primary_diagnosis_medicine_2",
    "secondary_diagnosis_medicine_1",
    "secondary_diagnosis_medicine_2"
]

# Maps the route value stored in the records to the matching label.
ROUTE_LABELS = {
    "EMERGENCY": "Emergency",
    "Doctor": "Doctor",
    "Pharmacist": "Pharmacy",
    "Retail": "Retail",
}

# ======================================================================
# FUNCTIONS KEPT
# ======================================================================
# keep original function names, parameters and return values.
# Apply to functions that are not class methods

# create a PatientRecord object with the following constants as its attributes.
def _patient_record() -> PatientRecord:
    # underscore prefix for internal use only
    return PatientRecord(
        RECORDS_CSV_PATH,
        SEED_RECORDS_CSV_PATH,
        RECORD_COLUMNS
    )


