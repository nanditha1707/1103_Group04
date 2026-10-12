from datetime import datetime

import pandas as pd
import os


# csv file used to store patient records
RECORDS_FILE="patient_records.csv"

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

    # get current date
    today = datetime.now().strftime("%Y-%m-%d")
    load_records()

    # check each patient
    for index, patient in records.iterrows():

        # match the queue number and current date
        if (
            patient["queue_number"]== queue_number
            and patient["date"]== today
        ):
            return patient.to_dict()

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

    try:
        # open patient records
        records = pd.read_csv(records_file)

    except FileNotFoundError:
        return 0

    count = 0

    # medicine fields from AI output
    medicine_fields=[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # check each patient
    for index, patient in records.iterrows():

        # only check records from selected date
        if patient["date"]== date:

            # check all medicine fields
            for field in medicine_fields:

                if str(patient[field]).lower()== medicine.lower():
                    count += 1

    return count

# get breakdown of medicines issued on a date
def get_medicine_breakdown(date):

    # dictionary to store medicine and count
    medicine_counts={}

    try:
        # open patient records
        records = pd.read_csv(records_file)

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
        records = pd.read_csv(records_file)

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