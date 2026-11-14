from datetime import datetime

from dotenv import load_dotenv

from ai_manager import AIManagerFactory
from app import constants
from app.menu import ExitAction, MainMenu, RegistrationAction
from app.portal import CurrentPatientQuery, HealthcarePortal, PastPatientQuery, ReportMenu
from app.queries import AllPatientsScope, PatientQueryHandler, QueryFilter, QueryResultPresenter, SinglePatientScope
from app.reports import MedicineBreakdownReport, MedicineCountReport, PatientTypeBreakdownReport
from data_manager import DataManager, DataManagerFactory, EncryptionKeyError
from io_manager import IOManager, IOManagerFactory
from io_manager.form import RegistrationFactory
from logic_manager import LogicManagerFactory

from .application import Application
from .startup_failure import StartupFailure
from .triage_pipeline import TriagePipeline


class ApplicationFactory:

    @staticmethod
    def create() -> Application:
        # The symptom list comes from a local CSV, 
        # so the one IO manager can be created before the data manager checks the encryption key.
        io = IOManagerFactory.create(DataManagerFactory.load_symptoms(), RegistrationFactory(constants.TIMEZONE))
        # A missing, malformed or wrong key, 
        # or an unreachable database stops the program here, before any patient record is touched.
        try:
            data = DataManagerFactory.create(clock=ApplicationFactory.__now)
        except EncryptionKeyError as error:
            message = constants.STARTUP_FAILED_MESSAGE.format(error=str(error))
            return StartupFailure(io, message)

        # load the ICD and HSA datasets once, when the program starts
        icd_df, hsa_df = data.get_cleaned_datasets()
        # Read the AI API keys from the local .env file
        load_dotenv(override=True)
        # The AI manager checks every AI answer against the same datasets that logic_manager routes with,
        # so every valid medicine can be routed
        ai = AIManagerFactory.create(icd_df, hsa_df)
        # Create the logic manager using the HSA dataset and data_manager for queue numbers.
        logic = LogicManagerFactory.create(hsa_df, data, ApplicationFactory.__now)

        triage_pipeline = TriagePipeline(screens=io, prompt=io, diagnoser=ai, router=logic, records=data)
        registration = RegistrationAction(io, triage_pipeline)
        healthcare_portal = ApplicationFactory.__create_healthcare_portal(io, data)
        return Application(MainMenu(io, [registration, healthcare_portal, ExitAction(io)]))

    @staticmethod
    def __now() -> datetime:
        """Return the current time in the clinic's timezone. Every manager
        reads the time from this one clock so they always agree on the date."""
        return datetime.now(constants.TIMEZONE)

    @staticmethod
    def __create_healthcare_portal(io: IOManager, data: DataManager) -> HealthcarePortal:
        filters = [
            QueryFilter(constants.PATIENT_INFO_FILTER_LABEL, constants.PATIENT_COLUMNS),
            QueryFilter(constants.MEDICAL_INFO_FILTER_LABEL, constants.MEDICAL_COLUMNS),
            QueryFilter(constants.AI_OUTPUT_FILTER_LABEL, constants.AI_OUTPUT_COLUMNS),
            QueryFilter(constants.ALL_RECORDS_FILTER_LABEL, data.get_record_columns())
        ]
        query_handler = PatientQueryHandler(
            io, filters, [SinglePatientScope(io, data), AllPatientsScope(data)], QueryResultPresenter(io, data)
        )
        reports = [MedicineCountReport(io, data), MedicineBreakdownReport(data), PatientTypeBreakdownReport(data)]
        return HealthcarePortal(io, [
            CurrentPatientQuery(data, query_handler),
            PastPatientQuery(io, query_handler),
            ReportMenu(io, io, reports)
        ])
