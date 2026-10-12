from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import os


# Import filepaths
base_dir= Path(__file__).parent  # find the directory path of the folder containing the currently running script.
dataset_dir= base_dir/ "datasets"

icd_file = dataset_dir / "icd_11.csv"
hsa_file = dataset_dir / "ListingofRegisteredTherapeuticProducts.csv"


# Load ICD Dataset
def load_icd_data():

    try:
        icd_df = pd.read_csv(
            icd_file,
            low_memory=False
        )

        return icd_df

    except FileNotFoundError:
        return None

    except pd.errors.ParserError:
        return None


# Load HSA Dataset
def load_hsa_data():

    try:
        hsa_df = pd.read_csv(
            hsa_file,
            low_memory=False
        )

        return hsa_df

    except FileNotFoundError:
        return None
    
    except pd.errors.ParserError:
        return None


# Clean ICD Dataset
def clean_icd_data(icd_df):

    # Keep only the disease title column
    icd_df = icd_df[
        [
            "Title"
        ]
    ].copy()


    # Rename column to make it clearer
    icd_df = icd_df.rename(
        columns={
            "Title": "DiseaseName"
        }
    )


    # Replace empty strings with NaN
    icd_df = icd_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )


    # Replace dash values with NaN
    icd_df = icd_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


    # Remove rows where disease name is missing
    icd_df = icd_df.dropna(
        subset=[
            "DiseaseName"
        ]
    )

    # Remove extra spaces
    icd_df["DiseaseName"] = (
        icd_df["DiseaseName"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicate diseases
    icd_df = icd_df.drop_duplicates()

    # Reset index
    icd_df = icd_df.reset_index(
        drop=True
    )


    return icd_df


# Clean HSA Dataset
def clean_hsa_data(hsa_df):

    # Keep only the required columns
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


    # Rename columns to clearer names
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


    # Replace empty strings with NaN
    hsa_df = hsa_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

    # Replace dash values with NaN
    hsa_df = hsa_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


    # Remove rows that are missing important information
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

    # Remove extra spaces
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

    # Remove duplicate rows
    hsa_df = hsa_df.drop_duplicates()

    # Reset index
    hsa_df = hsa_df.reset_index(
        drop=True
    )

    return hsa_df 


#Load the datasets
def get_cleaned_datasets():

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


# csv file used to store patient records
RECORDS_FILE="patient_records.csv"
# medicine fields from AI output
MEDICINE_FIELDS=[
    "primary_diagnosis_medicine_1",
    "primary_diagnosis_medicine_2",
    "secondary_diagnosis_medicine_1",
    "secondary_diagnosis_medicine_2"
]

# Load all records,
# or a empty df if the file doesn't exist yet
def load_records() -> pd.DataFrame:
    try:
        return pd.read_csv(RECORDS_FILE)
    except FileNotFoundError:
        return None


# save a completed patient record
def export_record(
    all_user_responses: dict,
    ai_output: dict,
    logic_result: dict
):
    # put all the patient information together
    patient_record = {}

    patient_record.update(all_user_responses)
    patient_record.update(ai_output)
    patient_record.update(logic_result)

    # change patient record into dataframe
    patient_record = pd.DataFrame([patient_record])

    # Appends the df to the csv, 
    # only write the header if the file is new.
    patient_record.to_csv(
        RECORDS_FILE,
        mode="a",
        header=not os.path.exists(RECORDS_FILE),
        index=False,
    )

# find patient using queue number
def get_patient_by_queue(queue_number):

    # Sets today to the current date
    today = datetime.now().strftime("%Y-%m-%d")
    #Loads the existing records. 
    # If the records do not exist, 
    # the function returns None.
    records = load_records()

    # Checks if records exist, if it does, 
    # continues with the block
    if records != None:
        # Iterates through the dataframes rows
        for _, patient in records.iterrows():

            # Searches for entry with a matching date and queue number.
            # Returns the first match, as Queue number is unique,
            # based on a day by day basis.
            if (
                patient["queue_number"]== queue_number
                and patient["date"]== today
            ):
                return patient.to_dict()
    # If there is no such patient, return None
    return None


# display patient information
def display_patient(patient):

    if patient is None:
        print("Patient not found.")
        return

    print("\nPATIENT INFORMATION")
    print("-------------------")

    print("Name:",patient["name"])
    print("Age:", patient["age"])
    print("Gender:", patient["gender"])
    print("Chest Pain:", patient["red_flag_chest_pain"])
    print("Breathing Issue:", patient["red_flag_breathing"])
    print("Stroke Symptoms:",patient["red_flag_stroke"])
    print("Self Harm:",patient["self_harm"])
    print("Symptoms:", patient["current_symptoms"])
    print("Symptom Onset:", patient["symptom_onset"])
    print("Chronic Conditions:", patient["chronic_conditions"])
    print("Current Medications:", patient["current_medications"])
    print("Drug Allergies:", patient["drug_allergies"])

    print("\nAI DIAGNOSIS")
    print("------------")

    print( "Primary Diagnosis:", patient["primary_diagnosis_ICD11_Title"])
    print("Primary Diagnosis Code:", patient["primary_diagnosis_ICD11_Code"])
    print("Secondary Diagnosis:", patient["secondary_diagnosis_ICD11_Title"])
    print("Secondary Diagnosis Code:", patient["secondary_diagnosis_ICD11_Code"])
    print("Primary Medicine 1:", patient["primary_diagnosis_medicine_1"])
    print("Primary Medicine 2:",patient["primary_diagnosis_medicine_2"])
    print("Secondary Medicine 1:", patient["secondary_diagnosis_medicine_1"])
    print("Secondary Medicine 2:", patient["secondary_diagnosis_medicine_2"])
    print("AI Confidence Score:",patient["ai_confidence_score"])

    print("\nROUTING INFORMATION")
    print("-------------------")

    print("Queue Number:", patient["queue_number"])
    print("Route:", patient["route"])
    print("Date:", patient["date"])
    print("Time:", patient["time"])

# get count of a specific medicine issued on a date
def get_medicine_count(date, medicine):
    records = load_records()
    count = 0

    # check each patient
    for index, patient in records.iterrows():

        # only check records from selected date
        if patient["date"]== date:

            # check all medicine fields
            for field in MEDICINE_FIELDS:

                if str(patient[field]).lower()== medicine.lower():
                    count += 1

    return count

# get breakdown of medicines issued on a date
def get_medicine_breakdown(date):

    # dictionary to store medicine and count
    medicine_counts={}

    try:
        # open patient records
        records = pd.read_csv(RECORDS_FILE)

    except FileNotFoundError:
        return medicine_counts

    # medicine fields from AI output
    medicine_fields =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # check each patient
    for index, patient in records.iterrows():

        # only check records from selected date
        if patient["date"]==date:

            # check all medicine fields
            for field in medicine_fields:

                medicine =patient[field]

                # only count if medicine is not empty
                if pd.notna(medicine):

                    if medicine in medicine_counts:
                        medicine_counts[medicine]+=1

                    else:
                        medicine_counts[medicine]=1

    return medicine_counts

# get breakdown of patient types for a date
def get_patient_type_breakdown(date):

    # start all counts at 0
    patient_types={
        "Emergency":0,
        "Doctor":0,
        "Pharmacy":0,
        "Retail":0
    }

    try:
        # open patient records
        records = pd.read_csv(RECORDS_FILE)

    except FileNotFoundError:
        return patient_types

    # check each patient
    for index, patient in records.iterrows():

        #only check records from selected date
        if patient["date"]==date:

            # priority patients count as emergency
            if str(patient["priority"])=="True":
                patient_types["Emergency"]+=1

            elif patient["route"]=="Doctor":
                 patient_types["Doctor"]+=1

            elif patient["route"]=="Pharmacist":
                 patient_types["Pharmacy"]+=1

            elif patient["route"]=="Retail":
                 patient_types["Retail"]+=1

    return patient_types