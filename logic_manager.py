# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
from pathlib import Path
import pandas as pd

# Saved patient records, used to work out queue numbers.
PATIENT_RECORDS_CSV_PATH = Path(__file__).resolve().parent / "datasets" / "patient_records.csv"


# ======================================================================
# MEDICINE FUNCTIONS
# ======================================================================
def get_medicines(ai_output: dict) -> list:
    """Return a list of the medicines the AI recommended, skipping any
    medicine fields that are empty."""
    ai_medicines = []

    # Keys where the medicines are stored in the AI output.
    medicine_keys =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # Go through each medicine key.
    for key in medicine_keys:

        # Get the medicine stored under the key.
        ai_medicine = ai_output.get(key)

        # Only add it if there is an medicine.
        if ai_medicine:
            ai_medicines.append(ai_medicine)

    # Return the list of medicines.
    return ai_medicines


def get_classification(ai_medicine: str, hsa_df: pd.DataFrame) -> str | None:
    """Look up the HSA classification of a medicine, e.g. Prescription
    Only. If the medicine matches several rows, the least restrictive
    classification is returned. This is because if the same medicine is
    available at a retail store, there is no need to go to a pharmacist
    or a doctor. Returns None if the medicine is not in the HSA dataset."""

    # HSA classifications ordered from least to most restrictive.
    classification_order = [
        "General Sale List",
        "Pharmacy Only",
        "Prescription Only"
    ]

    # Variable to store the least restrictive classification found so far.
    least_restrictive = None

    # Go through the HSA dataset one row at a time. The row number is used
    # to get the drug name and active ingredient from that same row.
    for row in range(len(hsa_df)):
        drug_name = hsa_df["DrugName"][row]
        ingredient = hsa_df["ActiveIngredients"][row]

        # Check if the AI medicine matches either field.
        if ai_medicine in drug_name or ai_medicine in ingredient:

            # Get the HSA classification from the same row.
            classification = hsa_df["Classification"][row]

            # Skip classifications that are not in the order list.
            if classification not in classification_order:
                continue

            # General Sale List is the least restrictive, so stop searching.
            if classification == classification_order[0]:
                return classification

            # Keep it if it is less restrictive than the one stored.
            if (least_restrictive is None
                    or classification_order.index(classification)
                    < classification_order.index(least_restrictive)):
                least_restrictive = classification

    # Return the least restrictive classification, or None if not found.
    return least_restrictive


# ======================================================================
# ROUTING FUNCTIONS
# ======================================================================
def is_emergency(ai_output: dict) -> bool:
    """Return True if the AI wrote EMERGENCY in either diagnosis
    explanation, otherwise return False."""

    # Keys where the AI explains each diagnosis.
    explanation_keys = [
        "primary_diagnosis_explanation",
        "secondary_diagnosis_explanation"
    ]

    # Go through each explanation.
    for key in explanation_keys:

        # Emergency if the explanation contains the word EMERGENCY.
        if "EMERGENCY" in str(ai_output.get(key, "")):
            return True

    return False


def decide_route(ai_output: dict, hsa_df: pd.DataFrame | None) -> str | None:
    """Decide where the patient should go: EMERGENCY, Doctor, Pharmacist
    or Retail. Returns None if the AI output failed, so the patient is
    not routed."""

    # AI output failed validation, so the patient is not routed because
    # the AI output is not reliable.
    if "error" in ai_output:
        return None

    # AI flagged an emergency, this overrides every other route.
    if is_emergency(ai_output):
        return "EMERGENCY"

    # Without HSA data the medicines cannot be checked, so see a doctor.
    if hsa_df is None:
        return "Doctor"

    # Get all medicines recomended by AI.
    ai_medicines=get_medicines(ai_output)

    # Variable to store if at least one pharmacy-only medicine is found.
    pharmacist_needed = False

    # Check each recommended medicine.
    for ai_medicine in ai_medicines:

        # Get the medicine classification from HSA data.
        classification = get_classification(ai_medicine, hsa_df)

        # Prescription only medicine requires doctor.
        if classification == "Prescription Only":
            return "Doctor"

        # Pharmacy only medicine requires pharmacist.
        if classification=="Pharmacy Only":
            pharmacist_needed=True

    # If no prescription medicine but a pharmacy only medicine was found.
    if pharmacist_needed:
        return "Pharmacist"

    # Otherwise patient can go to retail.
    return "Retail"


# ======================================================================
# QUEUE NUMBER FUNCTIONS
# ======================================================================
def get_queue_number(queue_type: str) -> str | None:
    """Give out the next queue number for today in the Doctor, Pharmacist
    or Urgent queue, e.g. D008, by checking the saved patient records.
    Returns None for any other queue type."""

    # Letter at the start of each queue number to differentiate.
    prefixes = {
        "Doctor": "D",
        "Pharmacist": "P",
        "Urgent": "U"
    }

    prefix = prefixes.get(queue_type)

    # "Retail" does not get a queue number.
    if prefix is None:
        return None

    # Get todays date.
    today=datetime.now().strftime("%Y-%m-%d")

    # Highest number already given out in this queue today.
    highest_number_today = 0

    try:
        # Read the saved patient records.
        # dtype=str keeps queue numbers like D001 as text.
        # keep_default_na=False turns blank cells into "" instead of NaN.
        records_df = pd.read_csv(PATIENT_RECORDS_CSV_PATH, dtype=str, keep_default_na=False)

        # Only look at todays patients.
        todays_df = records_df[records_df["date"] == today]

        # Checks in patient records for highest queue number today.
        # Then adds 1 to print new queue number.
        for existing_queue_number in todays_df["queue_number"]:

            # Only look at queue numbers in the same queue e.g. D001.
            if existing_queue_number.startswith(prefix):
                try:
                    # [1:] drops the letter e.g. "D007" -> "007".
                    # int() turns "007" into 7.
                    # max() keeps the highest number seen so far.
                    highest_number_today = max(
                        highest_number_today,
                        int(existing_queue_number[1:])
                    )

                # Skip queue numbers that are corrupted.
                except ValueError:
                    pass

    # If there are no saved records yet, the queue starts from 0.
    except FileNotFoundError:
        pass

    # If the file is empty, has no date/queue_number column,
    # or cannot be read, the queue starts from 0.
    except (pd.errors.EmptyDataError, pd.errors.ParserError, KeyError, OSError):
        pass

    # Return the next queue number e.g. D008.
    # :03d sets the minimum width to 3, so instead of D9 it is D009.
    return f"{prefix}{highest_number_today + 1:03d}"


# ======================================================================
# FINAL RESULT FUNCTION
# ======================================================================
def process_result(ai_output: dict, hsa_df: pd.DataFrame | None) -> dict:
    """Create the final domain result. Routes the patient, gives them a
    queue number and returns both with the current date and time."""

    # Where the patient goes.
    route=decide_route(
        ai_output,
        hsa_df
    )

    # Get current date and time.
    now=datetime.now()

    # Patient was not routed, so no queue number is given.
    if route is None:
        queue_number = None

    # Emergency route uses the urgent queue ( U queue ).
    elif route =="EMERGENCY":
        queue_number = get_queue_number("Urgent")

    # Docter route ( D queue ).
    elif route == "Doctor":
        queue_number =get_queue_number("Doctor")

    # Pharmacist route ( P queue ).
    elif route == "Pharmacist":
        queue_number = get_queue_number("Pharmacist")

    # Retail does not get a queue number.
    else:
        queue_number = None

    # Store final results.
    result ={
        "queue_number": queue_number,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "route": route
    }

    # Return final result.
    return result
