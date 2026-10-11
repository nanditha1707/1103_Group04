import csv
from pathlib import Path
from datetime import datetime

# folder where this file is located
base_dir= Path(__file__).parent

# csv file used to store patient records
records_file= base_dir/"patient_records.csv"

# save a completed patient record
def export_record(
    all_user_responses,
    ai_output,
    logic_result
):
    # put all the patient information together
    patient_record = {}

    patient_record.update(all_user_responses)
    patient_record.update(ai_output)
    patient_record.update(logic_result)

    # check if the file already exists
    file_exists = records_file.exists()

    # open csv file and add the patient record
    with open(records_file, "a", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=patient_record.keys()
        )

        # write the column names if the file is newly created
        if not file_exists:
            writer.writeheader()

        # add patient record
        writer.writerow(patient_record)

    return True

# find patient using queue number
def get_patient_by_queue(queue_number):

    # get current date
    today =datetime.now().strftime("%Y-%m-%d")

    # return none if there is no records file
    if not records_file.exists():
        return None

    # open csv file
    with open(records_file, "r", newline="") as file:

        reader=csv.DictReader(file)

        # check each patient
        for patient in reader:

            # match the queue number and current date
            if (
                patient["queue_number"]== queue_number
                and patient["date"]== today
            ):
                return patient
    return None