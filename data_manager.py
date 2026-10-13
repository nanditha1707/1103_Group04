# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import os
from datetime import datetime

import numpy as np
import pandas as pd

# File paths.
ICD_CSV_PATH = "datasets/icd11.csv"
HSA_CSV_PATH = "datasets/hsa.csv"

# CSV file used to store patient records.
# Same file logic_manager reads to work out queue numbers.
RECORDS_CSV_PATH = "datasets/patient_records.csv"

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
    "chest_pain",
    "breathing_difficulties",
    "signs_of_stroke",
    "self_harm",
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
    "chest_pain",
    "breathing_difficulties",
    "signs_of_stroke",
    "self_harm",
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


# ======================================================================
# DATASET LOADING FUNCTIONS
# ======================================================================
def load_icd_data():
    """Load the ICD-11 dataset. Return None if the file is missing or
    cannot be read."""

    try:
        icd_df = pd.read_csv(
            ICD_CSV_PATH,
            low_memory=False
        )

        return icd_df

    except FileNotFoundError:
        return None

    except pd.errors.ParserError:
        return None


def load_hsa_data():
    """Load the HSA dataset. Return None if the file is missing or
    cannot be read."""

    try:
        hsa_df = pd.read_csv(
            HSA_CSV_PATH,
            low_memory=False
        )

        return hsa_df

    except FileNotFoundError:
        return None
    
    except pd.errors.ParserError:
        return None


# ======================================================================
# DATASET CLEANING FUNCTIONS
# ======================================================================
def clean_icd_data(icd_df):
    """Return the ICD-11 dataset with only cleaned, unique disease names."""

    # Keep only the disease title column.
    icd_df = icd_df[
        [
            "Title"
        ]
    ].copy()


    # Rename the column to make it clearer.
    icd_df = icd_df.rename(
        columns={
            "Title": "DiseaseName"
        }
    )


    # Replace empty strings with NaN.
    icd_df = icd_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )


    # Replace dash values with NaN.
    icd_df = icd_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


    # Remove rows where the disease name is missing.
    icd_df = icd_df.dropna(
        subset=[
            "DiseaseName"
        ]
    )

    # Remove extra spaces.
    icd_df["DiseaseName"] = (
        icd_df["DiseaseName"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicate diseases.
    icd_df = icd_df.drop_duplicates()

    # Reset the index.
    icd_df = icd_df.reset_index(
        drop=True
    )


    return icd_df


def clean_hsa_data(hsa_df):
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


    # Replace empty strings with NaN.
    hsa_df = hsa_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

    # Replace dash values with NaN.
    hsa_df = hsa_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


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


def get_cleaned_datasets():
    """Load and clean both datasets. Return (None, None) if either
    dataset fails to load."""

    icd_df = load_icd_data()
    hsa_df = load_hsa_data()

    if icd_df is None or hsa_df is None:
        return None, None

    icd_df = clean_icd_data(
        icd_df
    )

    hsa_df = clean_hsa_data(
        hsa_df
    )

    return icd_df, hsa_df


# ======================================================================
# PATIENT RECORD FUNCTIONS
# ======================================================================
def load_records() -> pd.DataFrame:
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
    logic_result: dict,
    records_df: pd.DataFrame
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
        # Appends the df to the CSV,
        # only writing the header if the file is new.
        # 'a' append mode in pandas creates a new csv file if none exists.
        new_record_df.to_csv(
            RECORDS_CSV_PATH,
            mode="a",
            header=not os.path.exists(RECORDS_CSV_PATH),
            index=False,
            encoding="utf-8"
        )

    # The file is open in another program (e.g. Excel) or cannot be written.
    except OSError:
        return False
    
    # Only update the history after the save succeeded,
    # so it never contains a record that is missing from the CSV.
    if records_df is not None:
        records_df.loc[len(records_df)] = new_record_df.iloc[0]

    return True

def export_query(query_df: pd.DataFrame) -> bool:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    query_csv_path = f"datasets/query/query_{timestamp}.csv"
    try:
        # Appends the df to the CSV,
        # only writing the header if the file is new.
        # 'a' append mode in pandas creates a new csv file if none exists.
        query_df.to_csv(
            query_csv_path,
            mode="a",

            index=False,
            encoding="utf-8"
        )

    # The file is open in another program (e.g. Excel) or cannot be written.
    except OSError:
        return False
     
# ======================================================================
# PATIENT LOOKUP FUNCTIONS
# ======================================================================
def get_patient_filter(option: str)-> list:
    # Initialises filter to None,
    # and makes option a int
    option = int(option)
    filter= None
    if option == 1:
        filter=PATIENT_COLUMNS
    elif option == 2:
        filter=MEDICAL_COLUMNS
    elif option == 3:
        filter=AI_OUTPUT_COLUMN
    elif option == 4:
        filter= RECORD_COLUMNS
    else:
        print("This is not a valid option number.")
    return filter

def get_current_date()-> datetime:
    # grabs the current date
    today = datetime.now().strftime("%Y-%m-%d")
    return today

def get_patient_by_queue(queue_number,filter: list, today:datetime)-> pd.DataFrame:
    """Find today's patient with the given queue number. Return their
    record as a dict, or None if they are not found."""
    
    # Loads the existing records.
    # If the records do not exist,
    # the function returns None.
    records = load_records()

    # Checks if records exist. If they do,
    # continues with the block.
    if not records.empty:
        patient=records.query("queue_number == @queue_number and date == @today")
        return patient[filter]
    # If there is no such patient, return None.
    return None


# ======================================================================
# REPORT FUNCTIONS
# ======================================================================
def get_medicine_count(date, medicine):
    """Return how many times a medicine was issued on a given date."""
    records = load_records()
    count = 0

    # Check each patient.
    for index, patient in records.iterrows():

        # Only check records from the selected date.
        if patient["date"]== date:

            # Check all medicine fields.
            for field in MEDICINE_FIELDS:

                if str(patient[field]).lower()== medicine.lower():
                    count += 1

    return count


def get_medicine_breakdown(date):
    """Return a dict of each medicine issued on a given date and how
    many times it was issued."""

    # Dictionary to store each medicine and its count.
    medicine_counts={}

    try:
        # Open patient records.
        records = pd.read_csv(RECORDS_CSV_PATH)

    except FileNotFoundError:
        return medicine_counts

    # Medicine fields from AI output.
    medicine_fields =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # Check each patient.
    for index, patient in records.iterrows():

        # Only check records from the selected date.
        if patient["date"]==date:

            # Check all medicine fields.
            for field in medicine_fields:

                medicine =patient[field]

                # Only count if the medicine is not empty.
                if pd.notna(medicine):

                    if medicine in medicine_counts:
                        medicine_counts[medicine] += 1

                    else:
                        medicine_counts[medicine] = 1

    return medicine_counts


def get_patient_type_breakdown(date):
    """Return how many Emergency, Doctor, Pharmacy and Retail patients
    there were on a given date."""

    # Start all counts at 0.
    patient_types={
        "Emergency":0,
        "Doctor":0,
        "Pharmacy":0,
        "Retail":0
    }

    try:
        # Open patient records.
        records = pd.read_csv(RECORDS_CSV_PATH)

    except FileNotFoundError:
        return patient_types

    # Check each patient.
    for _, patient in records.iterrows():

        # Only check records from the selected date.
        if patient["date"]==date:

            if patient["route"]=="EMERGENCY":
                patient_types["Emergency"]+=1

            elif patient["route"]=="Doctor":
                 patient_types["Doctor"]+=1

            elif patient["route"]=="Pharmacist":
                 patient_types["Pharmacy"]+=1

            elif patient["route"]=="Retail":
                 patient_types["Retail"]+=1

    return patient_types
