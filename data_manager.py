# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import psycopg
from psycopg import sql
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Docker runs by default use UTC, so this is used to make Docker use SGT
# This matters for time and date generation for patient records 
SGT = ZoneInfo("Asia/Singapore")

DATABASE_URL = os.getenv("POSTGRESQL_CLOUD_DATABASE_URL")

# Folder paths, based on where this file is, not where the program is run from.
# Every module gets its file paths from here.
PROJECT_DIR = Path(__file__).resolve().parent
# Read-only datasets that ship with the app.
DATASETS_DIR = PROJECT_DIR / "datasets"
# Exported query results.
QUERY_DIR = PROJECT_DIR / "query"

# File paths.
ICD_CSV_PATH = DATASETS_DIR / "icd11.csv"
HSA_CSV_PATH = DATASETS_DIR / "hsa.csv"
SYMPTOMS_CSV_PATH = DATASETS_DIR / "symptoms_umls.csv"

# Fixed column order for a patient record, as shown to staff.
# The database stores these names in lowercase (Postgres lowercases
# unquoted names), so queries use column.lower() for the real name.
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


def load_symptoms() -> list[str]:
    """Reads the symptoms dataset. Returns all symptom names in
    uppercase since user input is uppercased before matching."""
    symptoms_dataframe = pd.read_csv(SYMPTOMS_CSV_PATH)
    symptoms_column = symptoms_dataframe["term"].str.upper()
    return symptoms_column.tolist()


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
# DATABASE FUNCTIONS
# ======================================================================
def fetch_rows(sql_statement: str | sql.Composed, parameters: tuple) -> list[tuple] | None:
    """Run a SELECT on the cloud database and return every row it found.
    Each call opens a new connection, so the rows always include records
    saved by other users. Return None if the database could not be
    reached or the query failed."""
    try:
        with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
            # psycopg fills in each %s with the matching parameter safely,
            # so user input is never pasted into the SQL itself.
            cursor.execute(sql_statement, parameters)
            return cursor.fetchall()
    except psycopg.Error:
        return None


# ======================================================================
# PATIENT RECORD FUNCTIONS
# ======================================================================
def join_symptoms(patient_record: dict) -> dict:
    """Join the symptoms list into one string, since the database
    column holds text, not a list."""

    symptoms = patient_record.get("current_symptoms")

    if isinstance(symptoms, list):
        patient_record["current_symptoms"] = ", ".join(symptoms)

    return patient_record


def export_record(all_user_responses: dict, ai_output: dict, logic_result: dict) -> str | None:
    """Save a completed patient record to the database.
    Return None if saved, or the error message if it could not be written."""

    # Step 1: Put all the patient information into one dict.
    all_patient_information = {}
    all_patient_information.update(all_user_responses)
    all_patient_information.update(ai_output)
    all_patient_information.update(logic_result)

    # Step 2: Turn the symptoms list into one string,
    all_patient_information = join_symptoms(all_patient_information)

    # Step 3: Build the record to save, one entry per column.
    # Only columns in RECORD_COLUMNS are kept, so extra keys like
    # (consent, refused, error) are left out.
    # A missing column is set to None, which the database saves as NULL.
    patient_record = {}
    for column in RECORD_COLUMNS:
        patient_record[column] = all_patient_information.get(column)

    # Step 4: export to cloud Database
    sql_statement = """
        INSERT INTO patient_records (
            date,
            time,
            queue_number,
            name,
            nric,
            gender,
            age,
            phone_number,
            pregnancy,
            current_symptoms,
            symptom_onset_days,
            chronic_conditions,
            current_medications,
            drug_allergies,
            primary_diagnosis_icd11_code,
            primary_diagnosis_icd11_title,
            primary_diagnosis_explanation,
            primary_diagnosis_medicine_1,
            primary_diagnosis_medicine_2,
            secondary_diagnosis_icd11_code,
            secondary_diagnosis_icd11_title,
            secondary_diagnosis_explanation,
            secondary_diagnosis_medicine_1,
            secondary_diagnosis_medicine_2,
            ai_confidence_score,
            route
        )
        VALUES (
            %(date)s,
            %(time)s,
            %(queue_number)s,
            %(name)s,
            %(nric)s,
            %(gender)s,
            %(age)s,
            %(phone_number)s,
            %(pregnancy)s,
            %(current_symptoms)s,
            %(symptom_onset_days)s,
            %(chronic_conditions)s,
            %(current_medications)s,
            %(drug_allergies)s,
            %(primary_diagnosis_ICD11_Code)s,
            %(primary_diagnosis_ICD11_Title)s,
            %(primary_diagnosis_explanation)s,
            %(primary_diagnosis_medicine_1)s,
            %(primary_diagnosis_medicine_2)s,
            %(secondary_diagnosis_ICD11_Code)s,
            %(secondary_diagnosis_ICD11_Title)s,
            %(secondary_diagnosis_explanation)s,
            %(secondary_diagnosis_medicine_1)s,
            %(secondary_diagnosis_medicine_2)s,
            %(ai_confidence_score)s,
            %(route)s
        )
    """

    try:
        with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
            cursor.execute(sql_statement, patient_record)
    except psycopg.Error as error:
        return f"{type(error).__name__} - {error}"

    return None

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
    today = datetime.now(SGT).strftime("%Y-%m-%d")
    return today

def build_selected_columns(columns: list[str]) -> sql.Composed:
    """Build the column list of a SELECT, e.g. name AS "name", ...
    The AS keeps the original names (e.g. primary_diagnosis_ICD11_Code)
    as the table headers instead of the lowercase database names.
    sql.Identifier quotes each name safely."""
    return sql.SQL(", ").join(
        sql.SQL("{} AS {}").format(sql.Identifier(column.lower()), sql.Identifier(column))
        for column in columns
    )


def get_patient_by_queue(
    queue_number: str,
    filter_columns: list[str],
    date: str
) -> pd.DataFrame | None:
    """Find the patient with the given queue number on the given date
    (YYYY-MM-DD) in the database. Return a DataFrame of their record
    with only the filter_columns, which is empty if no patient matches,
    or None if the database could not be reached."""

    sql_statement = sql.SQL(
        "SELECT {} FROM patient_records WHERE queue_number = %s AND date = %s"
    ).format(build_selected_columns(filter_columns))

    rows = fetch_rows(sql_statement, (queue_number, date))
    if rows is None:
        return None

    # The DataFrame is only used to print the table or export it to CSV.
    return pd.DataFrame(rows, columns=filter_columns)


def get_patients_by_date(filter_columns: list[str], date: str) -> pd.DataFrame | None:
    """Find every patient registered on the given date (YYYY-MM-DD) in
    the database, earliest first. Return a DataFrame with one row per
    patient, which is empty if there were no patients, or None if the
    database could not be reached."""

    # Each patient gets their own row, so the time and queue number are
    # added in front to tell the rows apart, unless the filter already
    # has them.
    identifier_columns = []
    for column in ["time", "queue_number"]:
        if column not in filter_columns:
            identifier_columns.append(column)
    columns = identifier_columns + filter_columns

    sql_statement = sql.SQL(
        "SELECT {} FROM patient_records WHERE date = %s ORDER BY time"
    ).format(build_selected_columns(columns))

    rows = fetch_rows(sql_statement, (date,))
    if rows is None:
        return None

    # The DataFrame is only used to print the table or export it to CSV.
    return pd.DataFrame(rows, columns=columns)

def export_query(query_df: pd.DataFrame) -> bool:
    """Save the query results to a new timestamped CSV in the query
    folder. Return True if saved, False if the file could not be
    written."""
    timestamp = datetime.now(SGT).strftime("%Y%m%d_%H%M%S")
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
# Each record has 4 medicine columns. unnest() turns them into 4 rows,
# one medicine per row, so they can be counted as a single column.
# Used in the FROM part of the medicine reports.
MEDICINES_PER_RECORD = """
    patient_records,
    unnest(ARRAY[
        primary_diagnosis_medicine_1,
        primary_diagnosis_medicine_2,
        secondary_diagnosis_medicine_1,
        secondary_diagnosis_medicine_2
    ]) AS medicine
"""


def get_medicine_count(medicine: str, date: str) -> dict[str, int] | None:
    """Return a dict with how many times a specific medicine was issued
    on a given date. Returns an empty dict if it was not issued, or None
    if the database could not be reached."""

    sql_statement = f"""
        SELECT COUNT(*)
        FROM {MEDICINES_PER_RECORD}
        WHERE date = %s AND medicine = %s
    """
    rows = fetch_rows(sql_statement, (date, medicine))
    if rows is None:
        return None

    # COUNT(*) always returns exactly one row with one value.
    times_issued = rows[0][0]
    if times_issued == 0:
        return {}
    return {medicine: times_issued}


def get_medicine_breakdown(date: str) -> dict[str, int] | None:
    """Return a dict of each medicine issued on a given date and how
    many times it was issued, most issued first. Returns None if the
    database could not be reached."""

    # Empty medicine columns are skipped so they are not counted.
    sql_statement = f"""
        SELECT medicine, COUNT(*) AS times_issued
        FROM {MEDICINES_PER_RECORD}
        WHERE date = %s AND medicine IS NOT NULL AND medicine <> ''
        GROUP BY medicine
        ORDER BY times_issued DESC, medicine
    """
    rows = fetch_rows(sql_statement, (date,))
    if rows is None:
        return None

    # Each row is (medicine, times_issued).
    return dict(rows)


def get_patient_type_breakdown(date: str) -> dict[str, int] | None:
    """Return how many Emergency, Doctor, Pharmacy and Retail patients
    there were on a given date. Returns None if the database could not
    be reached."""

    sql_statement = """
        SELECT route, COUNT(*)
        FROM patient_records
        WHERE date = %s
        GROUP BY route
    """
    rows = fetch_rows(sql_statement, (date,))
    if rows is None:
        return None

    # Each row is (route, count).
    route_counts = dict(rows)

    # Put the label and matching value into the dictionary, in the
    # order of ROUTE_LABELS, ignoring routes with no patients.
    patient_types = {}
    for route, label in ROUTE_LABELS.items():
        if route in route_counts:
            patient_types[label] = route_counts[route]

    return patient_types