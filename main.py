# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from ai_manager import AIManagerFactory
from app import constants
from app.portal import CurrentPatientQuery, HealthcarePortal, PastPatientQuery, ReportMenu
from app.queries import AllPatientsScope, PatientQueryHandler, QueryResultPresenter, SinglePatientScope
from app.reports import MedicineBreakdownReport, MedicineCountReport, PatientTypeBreakdownReport
from app.triage_pipeline import TriagePipeline
from data_manager import DataManagerFactory
from io_manager import IOManager
from logic_manager import LogicManagerFactory

from dotenv import load_dotenv

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

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
        healthcare_portal.run()

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
patient_query_handler = PatientQueryHandler(
    io, data, [SinglePatientScope(io, data), AllPatientsScope(data)], QueryResultPresenter(io, data)
)
healthcare_portal = HealthcarePortal(io, [
    CurrentPatientQuery(data, patient_query_handler),
    PastPatientQuery(io, patient_query_handler),
    ReportMenu(io, [MedicineCountReport(io, data), MedicineBreakdownReport(data), PatientTypeBreakdownReport(data)])
])

while True:
    # 1. I/O manager: collect the patient's answers
    answers=main_menu()
    if answers == constants.QUIT_SIGNAL:
        break
    if answers is None:
        continue

    triage_pipeline.process(answers)
