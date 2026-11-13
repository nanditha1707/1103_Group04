from pathlib import Path
from zoneinfo import ZoneInfo

# Docker runs by default use UTC so this is used to make Docker use SGT.
# This matters for time and date generation for patient records.
SGT = ZoneInfo("Asia/Singapore")

DATABASE_URL_ENV_VAR = "POSTGRESQL_CLOUD_DATABASE_URL"

# Folder paths
# Every module gets its file paths from here.
PROJECT_DIR = Path(__file__).resolve().parent.parent
# Read-only datasets
DATASETS_DIR = PROJECT_DIR / "datasets"
# Exported query results.
QUERY_DIR = PROJECT_DIR / "query"

# File paths.
ICD_CSV_PATH = DATASETS_DIR / "icd11.csv"
HSA_CSV_PATH = DATASETS_DIR / "hsa.csv"
SYMPTOMS_CSV_PATH = DATASETS_DIR / "symptoms_umls.csv"

# Fixed column order for a patient record
RECORD_COLUMNS = [
    "date",
    "time",
    "queue_number",
    "name",
    "nric",
    "gender",
    "birthdate",
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

IDENTIFIER_COLUMNS = [
    "time",
    "queue_number"
]

# Maps the route value stored in the records to the matching label.
ROUTE_LABELS = {
    "EMERGENCY": "Emergency",
    "Doctor": "Doctor",
    "Pharmacist": "Pharmacy",
    "Retail": "Retail",
}
