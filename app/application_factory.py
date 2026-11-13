from dotenv import load_dotenv

from ai_manager import AIManagerFactory
from app.menu import ExitAction, MainMenu, RegistrationAction
from app.portal import CurrentPatientQuery, HealthcarePortal, PastPatientQuery, ReportMenu
from app.queries import AllPatientsScope, PatientQueryHandler, QueryResultPresenter, SinglePatientScope
from app.reports import MedicineBreakdownReport, MedicineCountReport, PatientTypeBreakdownReport
from data_manager import DataManager, DataManagerFactory
from io_manager import IOManager
from logic_manager import LogicManagerFactory

from .application import Application
from .triage_pipeline import TriagePipeline


class ApplicationFactory:

    @staticmethod
    def create() -> Application:
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

        triage_pipeline = TriagePipeline(screens=io, prompt=io, diagnoser=ai, router=logic, records=data)
        registration = RegistrationAction(io, triage_pipeline)
        healthcare_portal = ApplicationFactory.__create_healthcare_portal(io, data)
        return Application(MainMenu(io, [registration, healthcare_portal, ExitAction(io)]))

    @staticmethod
    def __create_healthcare_portal(io: IOManager, data: DataManager) -> HealthcarePortal:
        query_handler = PatientQueryHandler(
            io, data, [SinglePatientScope(io, data), AllPatientsScope(data)], QueryResultPresenter(io, data)
        )
        reports = [MedicineCountReport(io, data), MedicineBreakdownReport(data), PatientTypeBreakdownReport(data)]
        return HealthcarePortal(io, [
            CurrentPatientQuery(data, query_handler),
            PastPatientQuery(io, query_handler),
            ReportMenu(io, io, reports)
        ])
