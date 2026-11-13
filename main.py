# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from ai_manager import AIManagerFactory
from app.menu import ExitAction, MainMenu, RegistrationAction
from app.portal import CurrentPatientQuery, HealthcarePortal, PastPatientQuery, ReportMenu
from app.queries import AllPatientsScope, PatientQueryHandler, QueryResultPresenter, SinglePatientScope
from app.reports import MedicineBreakdownReport, MedicineCountReport, PatientTypeBreakdownReport
from app.triage_pipeline import TriagePipeline
from data_manager import DataManagerFactory
from io_manager import IOManager
from logic_manager import LogicManagerFactory

from dotenv import load_dotenv

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
main_menu = MainMenu(io, [RegistrationAction(io, triage_pipeline), healthcare_portal, ExitAction(io)])

while main_menu.run_once():
    pass
