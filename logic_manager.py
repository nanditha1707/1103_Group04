from datetime import datetime

import pandas as pd

# saved patient records, used to work out queue numbers
PATIENT_RECORDS_CSV_PATH = "datasets/patient_records.csv"

# get all the medicine names from the AI output
def get_medicines(ai_output): 
    ai_medicines = []

    # keys where the medicines are stored in the AI output
    medicine_keys =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2", 
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # go through each medicine key
    for key in medicine_keys:

        # get the medicine stored under the key
        ai_medicine = ai_output.get(key)

        # only add it if there is an medicine
        if ai_medicine:
            ai_medicines.append(ai_medicine)

    # return the list of medicines
    return ai_medicines

# get HSA classification of medicine
def get_classification(ai_medicine, hsa_df):

    # go through the HSA dataset one row at a time. The row number is used
    # to get the drug name and active ingredient from that same row.
    for row in range(len(hsa_df)):
        drug_name = hsa_df["DrugName"][row]
        ingredient = hsa_df["ActiveIngredients"][row]

        # check if the AI medicine matches either field
        if ai_medicine in drug_name or ai_medicine in ingredient:

            # return the HSA classification from the same row
            return hsa_df["Classification"][row]

    # return None if medicine is not found
    return None

# check if the AI flagged the patient as an emergency
def is_emergency(ai_output):

    # keys where the AI explains each diagnosis
    explanation_keys = [
        "primary_diagnosis_explanation",
        "secondary_diagnosis_explanation"
    ]

    # go through each explanation
    for key in explanation_keys:

        # emergency if the explanation contains the word EMERGENCY
        if "EMERGENCY" in str(ai_output.get(key, "")):
            return True

    return False

# to decide where the patient should be routed to
def decide_route(answers_dict, ai_output, hsa_df):

    # AI flagged an emergency, this overrides every other route
    if is_emergency(ai_output):
        return "EMERGENCY"

    # AI bypass always routes the patient to a doctor
    if answers_dict.get("priority"):
        return "Doctor"

    # without HSA data the medicines cannot be checked, so see a doctor
    if hsa_df is None:
        return "Doctor"

    # get all medicines reccomended by AI
    ai_medicines=get_medicines(ai_output)

    # remember if at least one pharm only medicine is found
    pharmacist_needed = False

    # check each recommended medicine
    for ai_medicine in ai_medicines:

        # get the medicine classification from HSA data
        classification = get_classification(ai_medicine, hsa_df)

        # prescription only medicine requires doctor
        if classification == "Prescription Only":
            return "Doctor"

        # pharmacy only medicine requires pharmacist
        if classification=="Pharmacy Only":
            pharmacist_needed=True

    # if no prescription medicine but a pharmacy only medicine was found
    if pharmacist_needed:
        return "Pharmacist"

    # otherwise patient can go to retail
    return "Retail"

# generate next queue number based on routing
def get_queue_number(queue_type):

    # Letter at the start of each queue number to differentiate.
    prefixes = {
        "Doctor": "D",
        "Pharmacist": "P",
        "Urgent": "U"
    }

    prefix = prefixes.get(queue_type)

    # "Retail" does not get a queue number
    if prefix is None:
        return None

    # get todays date
    today=datetime.now().strftime("%Y-%m-%d")

    # highest number already given out in this queue today
    highest_number_today = 0

    try:
        # read the saved patient records
        # dtype=str keeps queue numbers like D001 as text
        # keep_default_na=False turns blank cells into "" instead of NaN
        records_df = pd.read_csv(
            PATIENT_RECORDS_CSV_PATH,
            dtype=str,
            keep_default_na=False
        )

        # only look at todays patients
        todays_df = records_df[records_df["date"] == today]

        # Checks in patient records for highest queue number today.
        # Then adds 1 to print new queue number.
        for existing_queue_number in todays_df["queue_number"]:

            # Only look at queue numbers in the same queue e.g. D001
            if existing_queue_number.startswith(prefix):
                try:
                    # [1:] drops the letter e.g. "D007" -> "007".
                    # int() turns "007" into 7.
                    # max() keeps the highest number seen so far.
                    highest_number_today = max(
                        highest_number_today,
                        int(existing_queue_number[1:])
                    )

                # skip queue numbers that are corrupted
                except ValueError:
                    pass

    # if there are no saved records yet, the queue starts from 0
    except FileNotFoundError:
        pass

    # if the file is empty, has no date/queue_number column,
    # or cannot be read, the queue starts from 0
    except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError, OSError):
        pass

    # return the next queue number e.g. D008
    # :03d sets the minimum width to 3, so instead of D9 it is D009.
    return f"{prefix}{highest_number_today + 1:03d}"

# final domain 
def process_result(
        answers_dict,
        ai_output,
        hsa_df,
):
    """Create the final domain result."""

    # where the patient goes
    route=decide_route(
        answers_dict,
        ai_output,
        hsa_df
    )

    # get current date and time
    now=datetime.now()

    # AI bypass route ( U queue )
    if answers_dict.get("priority"):
        queue_number =get_queue_number("Bypass")

    # docter route ( D queue )
    elif route =="Doctor":
        queue_number =get_queue_number("Doctor")

    # pharmacist route ( P queue )
    elif route =="Pharmacist":
        queue_number =get_queue_number("Pharmacist")

    # retail does not get a queue number
    else:
        queue_number = None

    # store final results
    result ={
        "queue_number": queue_number,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "route": route
    }

    # return final result
    return result