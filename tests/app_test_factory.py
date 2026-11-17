from collections.abc import Callable
from datetime import datetime

from app import ApplicationFactory
from app.interfaces import DiagnosisSource
from app.menu import MainMenu
from app.queries import PatientQueryHandler
from data_manager import DataManager, DataManagerFactory
from data_manager.storage import Database
from fakes import FakeCipher, FakeDiagnoser, FakeKeyCheckStore
from io_manager import IOManager, IOManagerFactory
from io_manager.console import Console
from io_manager.form import RegistrationFactory


class AppTestFactory:
    """
    Builds the real app classes through ApplicationFactory's own builders,
    but from a test console, a test database and a test diagnoser, so no
    test reaches the terminal, Postgres or a real AI model.

    No HSA dataset is loaded, so the router sends every non-emergency
    patient to a doctor.
    """

    ADMIN_PASSWORD = "Password"

    @staticmethod
    def create_data_manager(database: Database, clock: Callable[[], datetime] = ApplicationFactory.now) -> DataManager:
        """Build the real DataManager on the test database with a cipher
        that leaves values unchanged and a key check that always passes,
        so the test rows can stay in plain text. A test that does not pass
        a clock gets the clinic's real time, the same as the app."""
        return DataManagerFactory.create(clock, database, FakeCipher(), FakeKeyCheckStore())

    @staticmethod
    def create_io(console: Console, clock: Callable[[], datetime] = ApplicationFactory.now) -> IOManager:
        return IOManagerFactory.create([], RegistrationFactory(clock), console)

    @staticmethod
    def create_main_menu(
        io: IOManager, data: DataManager, diagnoser: DiagnosisSource | None = None, clock: Callable[[], datetime] = ApplicationFactory.now
    ) -> MainMenu:
        if diagnoser is None:
            diagnoser = FakeDiagnoser({})

        return ApplicationFactory.create_main_menu(io, data, diagnoser, None, AppTestFactory.ADMIN_PASSWORD, clock)

    @staticmethod
    def create_query_handler(io: IOManager, data: DataManager) -> PatientQueryHandler:
        return ApplicationFactory.create_query_handler(io, data)
