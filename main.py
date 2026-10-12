import ai_manager as ai
import data_manager as data
import io_manager as io
import logic_manager as logic

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()

while True:
    # 1. I/O manager: collect the patient's answers
    answers=io.main_menu()
    if answers == io.QUIT_SIGNAL:
        break
    if answers is None:
        continue

    # Filter answers so only non-personal information goes to the AI.
    answers_filtered = io.filter_answers(answers)

    # 2. AI manager: get a diagnosis and medicines
    ai_output = ai.get_ai_output(answers_filtered)
    print(ai_output)

    # the AI manager returns an "error" key when every AI model failed
    # failed AI output is not routed or saved, the patient sees staff
    if "error" in ai_output:
        io.print_ai_error()
        continue

    # 3. Logic manager: decide and print the route and queue number
    logic_result = logic.process_result(answers, ai_output, hsa_df)

    # 4. Data manager: save the completed record to patient_records.csv
    data.export_record(answers, ai_output, logic_result)
