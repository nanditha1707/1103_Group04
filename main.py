# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import pandas as pd

import ai_manager as ai
import data_manager as data
import logic_manager as logic
from io_manager import IOManager

QUIT_SIGNAL = -99
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

# Placeholder: the symptom list is loaded here for now.
# Uppercased since the patient's input is uppercased before matching.
symptom_terms = pd.read_csv(data.SYMPTOMS_CSV_PATH)["term"].str.upper().tolist()
io = IOManager(symptom_terms=symptom_terms)

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def patient_query_handler(date: str) -> str | None:
    """Ask for a filter option and queue number, then print or export
    that patient's record for the given date (YYYY-MM-DD).
    Return an error message if anything fails, otherwise None."""
    error = None
    filter_option= io.prompt_menu(FILTER_OPTIONS)
    option_error = io.validate_option(filter_option, len(FILTER_OPTIONS))
    if option_error is None:
        filter_list= data.get_patient_filter(filter_option)
        if filter_list is None:
            error = "This is not a valid option number!"
        else:
            queue = io.ask("Enter the Patient's Queue Number here: ").strip().upper()
            # Load the latest records so patients registered this session are found.
            records = data.load_records()
            query_response= data.get_patient_by_queue(records, queue, filter_list, date)
            # Wide results do not fit in the terminal, so they are
            # exported to a CSV instead of printed.
            next_action = data.print_or_export(filter_list)
            if query_response is not None and not query_response.empty:
                if next_action == "print":
                    io.show_table(query_response)
                elif next_action == "export" and not data.export_query(query_response):
                    error = "The query results could not be exported!"
            else:
                error ="There is no such patient, please enter a valid queue number!"
    else:
        error = option_error
    return error

def healthcare_portal_routing(option: str) -> None:
    """Run the healthcare portal option the user chose: query today's
    patients, query a past date, or show a report. Any error message is
    printed. Expects option to already be checked by
    io.validate_option."""
    option_number = int(option)
    error_message = None
    today = data.get_current_date()
    # Option 1: query a patient registered today.
    if option_number == 1:
        error_message = patient_query_handler(today)
    # Option 2: query a patient from a date the user enters.
    elif option_number == 2:
        datetime_answer = io.ask("Enter the Date here. (YYYY-MM-DD): ").strip()
        error_message = io.validate_date(datetime_answer)
        if error_message is None:
            error_message = patient_query_handler(datetime_answer)

    # Option 3: show one of the reports for a date the user enters.
    elif option_number == 3:
        report_option = io.prompt_menu(REPORT_OPTIONS,"Reports")
        option_error = io.validate_option(report_option, len(REPORT_OPTIONS))
        if option_error is None:
            date = io.ask("Enter the Date here. (YYYY-MM-DD): ").strip()
            date_error = io.validate_date(date)
            if date_error is None:
                previous_records_df = data.load_records()
                result = None
                header = ""
                if report_option == "1":
                    medicine = io.ask("Enter a medicine name: ").strip().upper()
                    result = data.get_medicine_count(previous_records_df,medicine, date)
                    header = ""
                elif report_option == "2":
                    result = data.get_medicine_breakdown(previous_records_df, date)
                    header = "Medicine Breakdown Report"
                elif report_option == "3":
                    result = data.get_patient_type_breakdown(previous_records_df, date)
                    header = "Patient Type Breakdown Report"
                else:
                    error_message = "This is not a valid option number!"
                # An empty report means nothing matched the date.
                if result:
                    io.show_table(result, header)
                elif error_message is None:
                    error_message= "There is no matching records for the given date!"
            else:
                error_message = date_error
        else:
            error_message = option_error
    else:
        error_message= "This is not a valid option number!"
    if error_message:
        io.show_message(error_message)

def main_menu() -> dict | int | None:
    """Show the main menu and run the option the user chose.

    Returns the patient's confirmed answers after a completed
    registration, QUIT_SIGNAL if the admin password was entered to
    exit, or None for anything else so the menu is shown again."""
    header = "Main Menu"
    main_menu_option= io.prompt_menu(MAIN_MENU_OPTIONS, header)
    if main_menu_option not in ["1","2","3"]:
        error = "This is not a valid option!"
        io.show_message(error)
    elif main_menu_option == "1":
        # Runs the questions and the confirmation screen. The IO manager
        # shows the confirmed or exit message itself, and returns None
        # if registration did not finish.
        return io.collect_registration()
    elif main_menu_option == "2":
        choice=io.prompt_menu(HEALTHCARE_PORTAL_OPTIONS)
        option_error= io.validate_option(choice, len(HEALTHCARE_PORTAL_OPTIONS))
        if option_error is None:
            healthcare_portal_routing(choice)
        else:
            io.show_message(option_error)

    elif main_menu_option == "3":
        inputted_pass=io.ask("Enter the exit code here: ")
        if inputted_pass == ADMIN_PASSWORD:
            io.show_message(MENU_EXIT_MESSAGE)
            return QUIT_SIGNAL
        else:
            error="This is not the right password!"
            io.show_message(error)

    return None

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()
# Copy the starter patient records on the first run
data.create_records_file_if_missing()

while True:
    # 1. I/O manager: collect the patient's answers
    answers=main_menu()
    if answers == QUIT_SIGNAL:
        break
    if answers is None:
        continue

    # Filter answers so only non-personal information goes to the AI.
    answers_filtered = io.filter_for_ai(answers)

    # 2. AI manager: get a diagnosis and medicines
    ai_output = ai.get_ai_output(answers_filtered, icd_df, hsa_df)

    # get_ai_output returns a dictionary when every AI model failed.
    # The key is "error". The value of the key is the message telling 
    # patients to seek assistance.
    if "error" in ai_output:
        io.show_message(ai_output["error"])
        continue

    # 3. Logic manager: decide and print the route and queue number
    logic_result = logic.process_result(ai_output, hsa_df)

    # 4. Data manager: save the completed record to patient_records.csv
    is_export=data.export_record(answers, ai_output, logic_result)
    if not is_export:
        error=("The program has encountered an error."
              "Please approach a nurse or clerk for manual registration.")
        io.show_message(error)
    else:
        # 5. I/O manager: tell the patient what to do next
        io.show_result(ai_output, logic_result)
