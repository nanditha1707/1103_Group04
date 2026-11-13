# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from ai_manager import AIManagerFactory
from app import constants
from app.queries import QueryResultPresenter
from app.triage_pipeline import TriagePipeline
from data_manager import DataManagerFactory
from io_manager import IOManager
from logic_manager import LogicManagerFactory

from dotenv import load_dotenv

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def patient_query_handler(date: str) -> str | None:
    """Ask for a filter option, then whether to look up one patient by
    queue number or every patient, and print or export the matching
    records for the given date (YYYY-MM-DD).
    Return an error message if anything fails, otherwise None."""
    error = None
    filter_option= io.prompt_menu(constants.FILTER_OPTIONS)
    option_error = io.validate_option(filter_option, len(constants.FILTER_OPTIONS))
    if option_error is None:
        filter_list= data.get_patient_filter(filter_option)
        if filter_list is None:
            error = "This is not a valid option number!"
        else:
            # Both options query the database directly, so patients
            # registered by other users are found too.
            scope_option = io.prompt_menu(constants.QUERY_SCOPE_OPTIONS)
            if scope_option == "1":
                queue = io.ask("Enter the Patient's Queue Number here: ").strip().upper()
                query_response= data.get_patient_by_queue(queue, filter_list, date)
                error = query_result_presenter.show(
                    query_response,
                    "There is no such patient, please enter a valid queue number!"
                )
            elif scope_option == "2":
                query_response = data.get_patients_by_date(filter_list, date)
                error = query_result_presenter.show(
                    query_response,
                    "There are no patient records for this date!"
                )
            else:
                error = "This is not a valid option number!"
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
        report_option = io.prompt_menu(constants.REPORT_OPTIONS,"Reports")
        option_error = io.validate_option(report_option, len(constants.REPORT_OPTIONS))
        if option_error is None:
            date = io.ask("Enter the Date here. (YYYY-MM-DD): ").strip()
            date_error = io.validate_date(date)
            if date_error is None:
                result = None
                header = ""
                if report_option == "1":
                    medicine = io.ask("Enter a medicine name: ").strip().upper()
                    result = data.get_medicine_count(medicine, date)
                    header = ""
                elif report_option == "2":
                    result = data.get_medicine_breakdown(date)
                    header = "Medicine Breakdown Report"
                elif report_option == "3":
                    result = data.get_patient_type_breakdown(date)
                    header = "Patient Type Breakdown Report"
                else:
                    error_message = "This is not a valid option number!"
                # A valid report returns None only if the database failed.
                if result is None and error_message is None:
                    error_message = constants.DATABASE_ERROR_MESSAGE
                # An empty report means nothing matched the date.
                elif result:
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
    main_menu_option= io.prompt_menu(constants.MAIN_MENU_OPTIONS, header)
    if main_menu_option not in ["1","2","3"]:
        error = "This is not a valid option!"
        io.show_message(error)
    elif main_menu_option == "1":
        # Runs the questions and the confirmation screen. The IO manager
        # shows the confirmed or exit message itself, and returns None
        # if registration did not finish.
        return io.collect_registration()
    elif main_menu_option == "2":
        choice=io.prompt_menu(constants.HEALTHCARE_PORTAL_OPTIONS)
        option_error= io.validate_option(choice, len(constants.HEALTHCARE_PORTAL_OPTIONS))
        if option_error is None:
            healthcare_portal_routing(choice)
        else:
            io.show_message(option_error)

    elif main_menu_option == "3":
        inputted_pass=io.ask("Enter the exit code here: ")
        if inputted_pass == constants.ADMIN_PASSWORD:
            io.show_message(constants.MENU_EXIT_MESSAGE)
            return constants.QUIT_SIGNAL
        else:
            error="This is not the right password!"
            io.show_message(error)

    return None

data = DataManagerFactory.create()

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()
# Read the AI API keys from the local .env file
load_dotenv(override=True)
# The AI manager checks every AI answer against the same datasets that
# logic_manager routes with, so every valid medicine can be routed
ai = AIManagerFactory.create(icd_df, hsa_df)
io = IOManager(symptom_terms=data.load_symptoms())
# Create the logic manager using the HSA dataset and data_manager for queue numbers.
logic = LogicManagerFactory.create(hsa_df, data)
triage_pipeline = TriagePipeline(io, ai, logic, data)
query_result_presenter = QueryResultPresenter(io, data)

while True:
    # 1. I/O manager: collect the patient's answers
    answers=main_menu()
    if answers == constants.QUIT_SIGNAL:
        break
    if answers is None:
        continue

    triage_pipeline.process(answers)
