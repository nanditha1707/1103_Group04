import json
from pathlib import Path

# folder where this file is located
base_dir= Path(__file__).parent

# json file used to store patient records
records_file= base_dir/"patient_records.json"

# save a completed patient record
def export_record(
    all_user_responses,
    ai_output,
    logic_result
):
    # put all the patient information together
    patient_record = {
        "user_responses":all_user_responses,
        "ai_output":ai_output,
        "logic_result":logic_result
    }

    records =[]

    # check if the file already exists
    if records_file.exists():
        try:
            # open and load existing records
            with open(records_file, "r") as file:
                records = json.load(file)

        # if the json file cannot be read properly
        except json.JSONDecodeError:
            records = []

    # add the new patient record
    records.append(patient_record)

    # save everything back into the file
    with open(records_file, "w") as file:
        json.dump(records, file, indent=4)

    return True