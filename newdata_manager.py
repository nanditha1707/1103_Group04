# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
from pathlib import Path

import pandas as pd

from dataset import Dataset
from hsa_dataset import HsaDataset
from icd_dataset import IcdDataset
from patient_record import PatientRecord
from patient_query import PatientQuery
from report_generator import ReportGenerator

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
# FUNCTIONS CREATING OBJECTS
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

# create a PatientQuery object.
def _patient_query(records: pd.DataFrame | None = None) -> PatientQuery:
    # underscore untilised for internal use 
    return PatientQuery(
        records,
        QUERY_DIR,
        {
            1: PATIENT_COLUMNS,
            2: MEDICAL_COLUMNS,
            3: AI_OUTPUT_COLUMN,
            4: RECORD_COLUMNS
        }
    )

# create a ReportGenerator object with the following constants as its attributes.
def _report_generator(records: pd.DataFrame) -> ReportGenerator:
    # underscore prefix for internal use only
    return ReportGenerator(records, MEDICINE_FIELDS, ROUTE_LABELS)


# ======================================================================
# FUNCTIONS USING DATASET, ICDDATASET AND HSADATASET CLASS METHODS
# ======================================================================

def load_dataset(csv_path: Path) -> pd.DataFrame | None:
    """Load a dataset CSV. Return None if the file is missing or
    cannot be read."""
    return Dataset.read_csv(csv_path)

def replace_blank_values(dataset_df: pd.DataFrame) -> pd.DataFrame:
    """Return the dataset with empty and dash values replaced by NaN,
    so they can be removed with dropna."""
    return Dataset.replace_blank_values(dataset_df)

def clean_icd_data(icd_df: pd.DataFrame) -> pd.DataFrame:
    """Return the ICD-11 dataset with only the disease codes and names,
    cleaned and without duplicates."""
    return IcdDataset(ICD_CSV_PATH).clean(icd_df)
 
def clean_hsa_data(hsa_df: pd.DataFrame) -> pd.DataFrame:
    """Return the HSA dataset with only the required drug columns,
    cleaned and without duplicates."""
    return HsaDataset(HSA_CSV_PATH).clean(hsa_df)
 
def get_cleaned_datasets() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load and clean the ICD-11 and HSA datasets. Either one is None if
    its file fails to load."""
    return (
        IcdDataset(ICD_CSV_PATH).get_cleaned(),
        HsaDataset(HSA_CSV_PATH).get_cleaned()
    )

