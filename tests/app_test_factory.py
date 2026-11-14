from collections.abc import Callable
from datetime import datetime

from app import constants
from app.interfaces import DiagnosisSource
from app.menu import ExitAction, MainMenu, RegistrationAction
from app.portal import CurrentPatientQuery, HealthcarePortal, PastPatientQuery, ReportMenu
from app.queries import AllPatientsScope, PatientQueryHandler, QueryFilter, QueryResultPresenter, SinglePatientScope
from app.reports import MedicineBreakdownReport, MedicineCountReport, PatientTypeBreakdownReport
from app.triage_pipeline import TriagePipeline
from data_manager import DataManager, DataManagerFactory
from data_manager.storage import Database
from fakes import FakeCipher, FakeDiagnoser, FakeKeyCheckStore
from io_manager import IOManager, IOManagerFactory
from io_manager.console import Console
from io_manager.form import RegistrationFactory
from logic_manager import LogicManagerFactory


class AppTestFactory:
    """
    Builds the real app classes the same way ApplicationFactory does, but
    from a test console, a test database and a test diagnoser, so no
    test reaches the terminal, Postgres or a real AI model.

    No HSA dataset is loaded, so the router sends every non-emergency
    patient to a doctor.
    """

    @staticmethod
    def now() -> datetime:
        """Return the current time in the clinic's timezone, like
        ApplicationFactory's clock."""
        return datetime.now(constants.TIMEZONE)

    @staticmethod
    def create_data_manager(database: Database, clock: Callable[[], datetime] | None = None) -> DataManager:
        """Build the real DataManager on the test database with a cipher
        that leaves values unchanged and a key check that always passes,
        so the test rows can stay in plain text. A test that does not pass
        a clock gets the clinic's real time, the same as the app."""
        if clock is None:
            clock = AppTestFactory.now
        return DataManagerFactory.create(clock, database, FakeCipher(), FakeKeyCheckStore())

    @staticmethod
    def create_io(console: Console) -> IOManager:
        return IOManagerFactory.create([], RegistrationFactory(constants.TIMEZONE), console)

    @staticmethod
    def create_main_menu(io: IOManager, data: DataManager, diagnoser: DiagnosisSource | None = None) -> MainMenu:
        if diagnoser is None:
            diagnoser = FakeDiagnoser({})

        logic = LogicManagerFactory.create(None, data, AppTestFactory.now)
        triage_pipeline = TriagePipeline(screens=io, prompt=io, diagnoser=diagnoser, router=logic, records=data)
        registration = RegistrationAction(io, triage_pipeline)
        healthcare_portal = AppTestFactory.create_healthcare_portal(io, data)
        return MainMenu(io, [registration, healthcare_portal, ExitAction(io)])

    @staticmethod
    def create_healthcare_portal(io: IOManager, data: DataManager) -> HealthcarePortal:
        query_handler = AppTestFactory.create_query_handler(io, data)
        reports = [MedicineCountReport(io, data), MedicineBreakdownReport(data), PatientTypeBreakdownReport(data)]
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
        scopes = [SinglePatientScope(io, data), AllPatientsScope(data)]
        return PatientQueryHandler(io, filters, scopes, QueryResultPresenter(io, data))
