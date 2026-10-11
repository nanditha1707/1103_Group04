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