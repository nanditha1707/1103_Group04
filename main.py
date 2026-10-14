# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import ai_manager as ai
import data_manager as data
import io_manager as io
import logic_manager as logic

ADMIN_PASSWORD = "Password"
MENU_EXIT_MESSAGE = "Admin Password Inputted, Exiting Program Now!"
MAIN_MENU_OPTIONS = ["1. Patient Registration",
                     "2. Healthcare Professional Portal",
                     "3. Exit"]
HEALTHCARE_PORTAL_OPTIONS = [
    "1. Query Current Patient Information",
    "2. Query Past Patient Information",
    "3. Reports",
                             ]
FILTER_OPTIONS =[
    "1. Patient Information", 
    "2. Medical Information", 
    "3. AI Ouput Information", 
    "4. All Records"
                 ]

REPORT_OPTIONS = [
    "1. Specific Medicine Count",
    "2. Medicine Breakdown",
    "3. Patient Type Breakdown"
]


# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def patient_query_handler(date) ->str | None:
    error = None
    filter_option= io.dynamic_menu_print(FILTER_OPTIONS)
    option_error = io.validate_option(filter_option)
    if option_error is None:
        filter= data.get_patient_filter(filter_option)
        if filter is None:
            error = "This is not a valid option number!"
        else:
            queue = input("Enter the Patient's Queue Number here.").strip().upper()
            # Load the latest records so patients registered this session are found.
            records = data.load_records()
            query_response= data.get_patient_by_queue(records, queue, filter, date)
            if query_response is not None and not query_response.empty:
                io.print_df_and_reports(query_response)
            else:
                error ="There is no such patient, please enter a valid queue number!"
    else:
        error = option_error
    return error

def healthcare_portal_routing(option:str):
    option = int(option)
    error_message = None
    today = data.get_current_date()
    if option == 1:
        error_message = patient_query_handler(today)
    if option == 2:
        datetime_answer = input("Enter the Date here. (YYYY-MM-DD): ").strip()
        error_message = io.validate_date(datetime_answer)
        if error_message is None:
            error_message = patient_query_handler(datetime_answer)

    if option == 3:
        report_option = io.dynamic_menu_print(REPORT_OPTIONS,"Reports")
        option_error = io.validate_option(report_option)
        if option_error is None:
            date = input("Enter the Date here. (YYYY-MM-DD): ").strip()
            date_error = io.validate_date(date)
            if date_error is None:
                records = data.load_records()

                if report_option == "1":
                    medicine = input("Enter a medicine name: ").strip().upper()
                    result = data.get_medicine_count(previous_records_df,medicine, date)
                    header = ""
                elif report_option == "2":
                    result = data.get_medicine_breakdown(previous_records_df, date)
                    header = "Medicine Breakdown Report"
                elif report_option == "3":
                    result = data.get_patient_type_breakdown(previous_records_df, date)
                    header = "Patient Type Breakdown Report"
                if result:
                    io.print_df_and_reports(result, header)
                else:
                    error_message= "There is no matching records for the given date!"
            else:
                error_message = date_error
        else:
            error_message = option_error

    if error_message:
        io.print_message(error_message)




def main_menu():
    header = "Main Menu"
    main_menu_option= io.dynamic_menu_print(MAIN_MENU_OPTIONS, header)
    if main_menu_option not in ["1","2","3"]:
        error = "This is not a valid option!"
        io.print_message(error)
    elif main_menu_option == "1":
        all_answers = io.run_questions()
        if all_answers is None:
            return None
        else:
            confirmed = io.confirm_inputs(all_answers)
            if confirmed:
                confirm_message = "Thank you for confirming your inputs."
                print(confirm_message)
                return all_answers
            else:
                error = io.REG_EXIT_MESSAGE
                io.print_message(error)
    elif main_menu_option == "2":
        choice=io.dynamic_menu_print(HEALTHCARE_PORTAL_OPTIONS)
        option_error= io.validate_option(choice)
        if option_error is None:
            healthcare_portal_routing(choice)
        else:
            io.print_message(option_error)

    elif main_menu_option == "3":
        inputted_pass=input("Enter the exit code here: ")
        if inputted_pass == ADMIN_PASSWORD:
            io.print_message(MENU_EXIT_MESSAGE)
            return io.QUIT_SIGNAL
        else:
            error="This is not the right password!"
            io.print_message(error)

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()
# Copy the starter patient records on the first run
data.create_records_file_if_missing()
#Load the previous entry records
previous_records_df= data.load_records()

while True:
    # 1. I/O manager: collect the patient's answers
    answers=main_menu()
    if answers == io.QUIT_SIGNAL:
        break
    if answers is None:
        continue

    # Filter answers so only non-personal information goes to the AI.
    answers_filtered = io.filter_answers(answers)

    # 2. AI manager: get a diagnosis and medicines
    ai_output = ai.get_ai_output(answers_filtered)

    # get_ai_output returns a dictionary when every AI model failed.
    # The key is "error". The value of the key is the message telling 
    # patients to seek assistance.
    if "error" in ai_output:
        io.print_message(ai_output["error"])
        continue

    # 3. Logic manager: decide and print the route and queue number
    logic_result = logic.process_result(ai_output, hsa_df)

    # 4. Data manager: save the completed record to patient_records.csv
    is_export=data.export_record(answers, ai_output, logic_result, previous_records_df)
    if not is_export:
        error=("The program has encountered an error."
              "Please approach a nurse or clerk for manual registration.")
        io.print_message(error)
    else:
        # 5. I/O manager: tell the patient what to do next
        io.print_result(ai_output, logic_result)
