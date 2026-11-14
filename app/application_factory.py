import os
from collections.abc import Callable
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from ai_manager import AIManagerFactory
from app import constants
from app.interfaces import DiagnosisSource, Runnable
from app.menu import ExitAction, MainMenu, PasswordGate, PasswordProtectedAction, RegistrationAction
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
    def create() -> Runnable:
        # Read the database URL, encryption key, AI API keys and admin password from the local .env file
        load_dotenv(override=True)
        # The symptom list comes from a local CSV, 
        # so the one IO manager can be created before the data manager checks the encryption key.
        io = IOManagerFactory.create(DataManagerFactory.load_symptoms(), RegistrationFactory(ApplicationFactory.now))
        # A missing, malformed or wrong key, 
        # or an unreachable database stops the program here, before any patient record is touched.
        try:
            data = DataManagerFactory.create(clock=ApplicationFactory.now)
        except EncryptionKeyError as error:
            message = constants.STARTUP_FAILED_MESSAGE.format(error=str(error))
            return StartupFailure(io, message)

        admin_password = os.getenv(constants.ADMIN_PASSWORD_ENV_VAR)
        if not admin_password:
            return StartupFailure(io, constants.ADMIN_PASSWORD_MISSING_MESSAGE)

        # load the ICD and HSA datasets once, when the program starts
        icd_df, hsa_df = data.get_cleaned_datasets()
        # The AI manager checks every AI answer against the same datasets that logic_manager routes with,
        # so every valid medicine can be routed
        ai = AIManagerFactory.create(icd_df, hsa_df)
        return Application(ApplicationFactory.create_main_menu(io, data, ai, hsa_df, admin_password, ApplicationFactory.now))

    @staticmethod
    def now() -> datetime:
        """Return the current time in the clinic's timezone. Every manager
        reads the time from this one clock so they always agree on the date."""
        return datetime.now(constants.TIMEZONE)

    @staticmethod
    def create_main_menu(
        io: IOManager, data: DataManager, diagnoser: DiagnosisSource, hsa_df: pd.DataFrame | None, admin_password: str, clock: Callable[[], datetime]
    ) -> MainMenu:
        # Create the logic manager using the HSA dataset and data_manager for queue numbers.
        logic = LogicManagerFactory.create(hsa_df, data, clock)
        gate = PasswordGate(io, admin_password)

        triage_pipeline = TriagePipeline(screens=io, prompt=io, diagnoser=diagnoser, router=logic, records=data)
        registration = RegistrationAction(io, triage_pipeline)
        healthcare_portal = ApplicationFactory.create_healthcare_portal(io, data)
        protected_portal = PasswordProtectedAction(healthcare_portal, gate)
        return MainMenu(io, [registration, protected_portal, ExitAction(io, gate)])

    @staticmethod
    def create_healthcare_portal(io: IOManager, data: DataManager) -> HealthcarePortal:
        query_handler = ApplicationFactory.create_query_handler(io, data)
        reports = [MedicineCountReport(data), MedicineBreakdownReport(data), PatientTypeBreakdownReport(data)]
        return HealthcarePortal(io, [
            CurrentPatientQuery(data, query_handler),
            PastPatientQuery(io, query_handler),
            ReportMenu(io, io, reports)
        ])

    @staticmethod
    def create_query_handler(io: IOManager, data: DataManager) -> PatientQueryHandler:
        filters = [
            QueryFilter(constants.PATIENT_INFO_FILTER_LABEL, constants.PATIENT_COLUMNS),
            QueryFilter(constants.MEDICAL_INFO_FILTER_LABEL, constants.MEDICAL_COLUMNS),
            QueryFilter(constants.AI_OUTPUT_FILTER_LABEL, constants.AI_OUTPUT_COLUMNS),
            QueryFilter(constants.ALL_RECORDS_FILTER_LABEL, data.get_record_columns())
        ]
        scopes = [SinglePatientScope(data), AllPatientsScope(data)]
        return PatientQueryHandler(io, filters, scopes, QueryResultPresenter(io, data))
