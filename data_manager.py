# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
from pathlib import Path
import shutil

import numpy as np
import pandas as pd

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
# DATASET LOADING FUNCTIONS
# ======================================================================
def load_dataset(csv_path: Path) -> pd.DataFrame | None:
    """Load a dataset CSV. Return None if the file is missing or
    cannot be read."""

    try:
        return pd.read_csv(
            csv_path,
            low_memory=False
        )

    except (FileNotFoundError, pd.errors.ParserError):
        return None


# ======================================================================
# DATASET CLEANING FUNCTIONS
# ======================================================================
def replace_blank_values(dataset_df: pd.DataFrame) -> pd.DataFrame:
    """Return the dataset with empty and dash values replaced by NaN,
    so they can be removed with dropna."""

    # Replace empty strings with NaN.
    dataset_df = dataset_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

    # Replace dash values with NaN.
    dataset_df = dataset_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )

    return dataset_df


def clean_icd_data(icd_df: pd.DataFrame) -> pd.DataFrame:
    """Return the ICD-11 dataset with only the disease codes and names,
    cleaned and without duplicates."""

    # Keep only the code and disease title columns.
    icd_df = icd_df[
        [
            "Code",
            "Title"
        ]
    ].copy()


    # Rename the title column to make it clearer.
    icd_df = icd_df.rename(
        columns={
            "Title": "DiseaseName"
        }
    )


    icd_df = replace_blank_values(icd_df)


    # Remove rows where the code or disease name is missing.
    icd_df = icd_df.dropna(
        subset=[
            "Code",
            "DiseaseName"
        ]
    )

    # Remove extra spaces and uppercase, to match the formatted AI output.
    icd_df["Code"] = (
        icd_df["Code"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    icd_df["DiseaseName"] = (
        icd_df["DiseaseName"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Remove duplicate diseases.
    icd_df = icd_df.drop_duplicates()

    # Reset the index.
    icd_df = icd_df.reset_index(
        drop=True
    )


    return icd_df


def clean_hsa_data(hsa_df: pd.DataFrame) -> pd.DataFrame:
    """Return the HSA dataset with only the required drug columns,
    cleaned and without duplicates."""

    # Keep only the required columns.
    hsa_df = hsa_df[
        [
            "Productname",
            "Dosageform",
            "Strength",
            "Activeingredients",
            "ATCCode",
            "Forensicclassification"
        ]
    ].copy()


    # Rename columns to clearer names.
    hsa_df = hsa_df.rename(
        columns={
            "Productname": "DrugName",
            "Dosageform": "Dosage",
            "Strength": "Strength",
            "Activeingredients": "ActiveIngredients",
            "ATCCode": "ATCCode",
            "Forensicclassification": "Classification"
        }
    )


    hsa_df = replace_blank_values(hsa_df)


    # Remove rows that are missing important information.
    hsa_df = hsa_df.dropna(
        subset=[
            "DrugName",
            "Dosage",
            "Strength",
            "ActiveIngredients",
            "ATCCode",
            "Classification"
        ]
    )

    # Remove extra spaces.
    hsa_df["DrugName"] = (
        hsa_df["DrugName"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    hsa_df["Dosage"] = (
        hsa_df["Dosage"]
        .astype(str)
        .str.strip()
    )

    hsa_df["Strength"] = (
        hsa_df["Strength"]
        .astype(str)
        .str.strip()
    )

    hsa_df["ActiveIngredients"] = (
        hsa_df["ActiveIngredients"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    hsa_df["ATCCode"] = (
        hsa_df["ATCCode"]
        .astype(str)
        .str.strip()
    )

    hsa_df["Classification"] = (
        hsa_df["Classification"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicate rows.
    hsa_df = hsa_df.drop_duplicates()

    # Reset the index.
    hsa_df = hsa_df.reset_index(
        drop=True
    )

    return hsa_df 


def get_cleaned_datasets() -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    """Load and clean the ICD-11 and HSA datasets. Either one is None if
    its file fails to load."""

    icd_df = load_dataset(ICD_CSV_PATH)
    hsa_df = load_dataset(HSA_CSV_PATH)

    if icd_df is not None:
        icd_df = clean_icd_data(icd_df)

    if hsa_df is not None:
        hsa_df = clean_hsa_data(hsa_df)

    return icd_df, hsa_df


# ======================================================================
# PATIENT RECORD FUNCTIONS
# ======================================================================
def create_records_file_if_missing() -> None:
    """Copy the starter records into the records folder if there is no
    patient records CSV yet. Existing records are never overwritten."""
    if RECORDS_CSV_PATH.exists():
        return

    try:
        RECORDS_DIR.mkdir(exist_ok=True)
        # Read the seed file first, so if it is missing the records
        # file is never created.
        # "b" copies the bytes exactly in binary mode, so copy is
        # identical to the seed.
        with open(SEED_RECORDS_CSV_PATH, "rb") as seed_file:
            seed_contents = seed_file.read()

        # Create the records file and write the seed contents into it.
        with open(RECORDS_CSV_PATH, "wb") as records_file:
            records_file.write(seed_contents)

    # The seed file is missing or the records folder cannot be written.
    # The program still runs and starts with no records.
    except OSError:
        pass


def load_records() -> pd.DataFrame | None:
    """Load all patient records. Return None if the file does not
    exist yet."""
    try:
        return pd.read_csv(RECORDS_CSV_PATH)
    except FileNotFoundError:
        return None


def join_symptoms(patient_record: dict) -> dict:
    """Join the symptoms list into one string, since a CSV cell cannot
    hold a list."""

    symptoms = patient_record.get("current_symptoms")

    if isinstance(symptoms, list):
        patient_record["current_symptoms"] = ", ".join(symptoms)

    return patient_record


def export_record(
    all_user_responses: dict,
    ai_output: dict,
    logic_result: dict
) -> bool:
    """Save a completed patient record to the patient records CSV.
    Return True if saved, False if the file could not be written."""
    # Put all the patient information together.
    patient_record = {}

    patient_record.update(all_user_responses)
    patient_record.update(ai_output)
    patient_record.update(logic_result)

    # Join the symptoms list into one cell.
    patient_record = join_symptoms(patient_record)

    # Build the CSV row from RECORD_COLUMNS only, in that order.
    # Extra keys (consent, refused, error) are left out.
    # Missing columns are set to None so the cell stays blank.
    csv_row = {}

    for column in RECORD_COLUMNS:
        csv_row[column] = patient_record.get(column)

    # Change the row into a one-row dataframe.
    new_record_df = pd.DataFrame([csv_row])

    try:
        # Creates the records folder if it does not exist yet.
        RECORDS_DIR.mkdir(exist_ok=True)

        # Appends the df to the CSV,
        # only writing the header if the file is new.
        # 'a' append mode in pandas creates a new csv file if none exists.
        new_record_df.to_csv(
            RECORDS_CSV_PATH,
            mode="a",
            header=not RECORDS_CSV_PATH.exists(),
            index=False,
            encoding="utf-8"
        )

    # The file is open in another program (e.g. Excel) or cannot be written.
    except OSError:
        return False

    return True

# ======================================================================
# PATIENT LOOKUP FUNCTIONS
# ======================================================================
def get_patient_filter(option: str) -> list[str] | None:
    """Return the record columns for a filter menu option (1 to 4).
    Return None for any other option number. Expects option to already
    be checked as a positive whole number by io_manager.validate_option."""
    # Initialises filter to None,
    # and makes option a int
    option_number = int(option)
    filter_columns = None
    if option_number == 1:
        filter_columns=PATIENT_COLUMNS
    elif option_number == 2:
        filter_columns=MEDICAL_COLUMNS
    elif option_number == 3:
        filter_columns=AI_OUTPUT_COLUMN
    elif option_number == 4:
        filter_columns= RECORD_COLUMNS
    return filter_columns

def get_current_date() -> str:
    """Return today's date as YYYY-MM-DD, the same format as the date
    column in the patient records."""
    # grabs the current date
    today = datetime.now().strftime("%Y-%m-%d")
    return today

def get_patient_by_queue(
    records: pd.DataFrame | None,
    queue_number: str,
    filter_columns: list[str],
    today: str
) -> pd.DataFrame | None:
    """Find the patient with the given queue number on the given date.
    Return a DataFrame of their record with only the filter_columns,
    which is empty if no patient matches, or None if there are no
    records."""

    # Checks if records exist. If they do,
    # continues with the block.
    if records is not None and not records.empty:
        # @ lets query use the local variables queue_number and today.
        patient=records.query("queue_number == @queue_number and date == @today")
        return patient[filter_columns]
    # If there is no such patient, return None.
    return None

def print_or_export(filter_columns: list[str]) -> str:
    """Return "print" if a table with these columns fits in the
    terminal, otherwise "export" so it is saved to a CSV instead."""
    # Each column is at least 10 characters wide (the table's
    # maxcolwidths), but a long column name needs more than that.
    width_needed= len(filter_columns)*10
    header_width_needed = sum(len(item) for item in filter_columns)
    width_needed = max(width_needed, header_width_needed)
    terminal_width=shutil.get_terminal_size().columns
    if terminal_width >= width_needed:
        return "print"
    else:
        return "export"

def export_query(query_df: pd.DataFrame) -> bool:
    """Save the query results to a new timestamped CSV in the query
    folder. Return True if saved, False if the file could not be
    written."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query_csv_path = QUERY_DIR / f"query_{timestamp}.csv"
    try:
        # Creates the query folder if it does not exist yet.
        QUERY_DIR.mkdir(exist_ok=True)

        # Writes the df to a new CSV file with a header.
        # The timestamp in the file name keeps each export separate.
        query_df.to_csv(
            query_csv_path,
            mode="w",
            index=False,
            encoding="utf-8"
        )

    # The file is open in another program (e.g. Excel) or cannot be written.
    except OSError:
        return False

    return True


# ======================================================================
# REPORT FUNCTIONS
# ======================================================================
def get_medicine_count(records: pd.DataFrame, medicine: str, date: str) -> dict[str, int]:
    """Return a dict with how many times a specific medicine was issued
    on a given date. Returns an empty dict if it was not issued."""

    # Filter to the selected date once.
    day_records = records.loc[records["date"] == date, MEDICINE_FIELDS]

    # Flatten all medicine columns into one Series, drop empties, and count.
    medicine_counts = day_records.stack().value_counts()

    # Keep only the requested medicine, if it appears at all.
    if medicine in medicine_counts.index:
        return {medicine: int(medicine_counts[medicine])}

    return {}


def get_medicine_breakdown(records: pd.DataFrame, date: str) -> dict:
    """Return a dict of each medicine issued on a given date and how
    many times it was issued."""

    # Filter to the selected date once.
    day_records = records.loc[records["date"] == date, MEDICINE_FIELDS]

    # Flatten all medicine columns into one Series, drop empties, and count.
    medicine_counts = day_records.stack().value_counts()

    # Returns medicine counts as a dictionary
    return medicine_counts.to_dict()


def get_patient_type_breakdown(records: pd.DataFrame, date: str) -> dict[str, int]:
    """Return how many Emergency, Doctor, Pharmacy and Retail patients
    there were on a given date."""

    # Creates a mask to filter the df by, 
    # and filters the df for matching rows.
    is_on_date = records["date"] == date
    records_on_date = records[is_on_date]
    # Get the count for how many times each route type appears.
    route_counts = records_on_date["route"].value_counts()

    # Put the label and matching value into the dictionary, 
    # ignoring any entries with no value.
    patient_types = {}
    for route, label in ROUTE_LABELS.items():
        if route in route_counts:
            patient_types[label] = int(route_counts[route])

    return patient_types