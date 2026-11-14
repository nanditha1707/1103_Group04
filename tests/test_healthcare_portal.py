import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import constants
from app.portal import CurrentPatientQuery, PastPatientQuery
from app_test_factory import AppTestFactory
from data_manager import DataManagerFactory
from fakes import FakeConsole, FakeDatabase
from io_manager import constants as io_constants


class TestHealthcarePortal:
    TODAY = "2026-10-14"
    SCOPE_OPTIONS = 2

    @staticmethod
    def __query_handler(console, database):
        io = AppTestFactory.create_io(console)
        data = DataManagerFactory.create(database)

        return AppTestFactory.create_query_handler(io, data)

    def test_current_patient_found(self):

        console = FakeConsole(["1", "1", "D001"])
        database = FakeDatabase([
            ("NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111")
        ])
        query_handler = self.__query_handler(console, database)

        result = query_handler.handle(
            self.TODAY
        )

        print("\nSCENARIO: Existing Patient Query")
        print("Queue: D001")
        print("Expected Patient: NANI")
        print("Actual:")
        print(console.shown[-1])

        assert result is None
        assert "NANI" in console.shown[-1]
        assert "T0111111C" in console.shown[-1]
        assert database.fetched_parameters == [("D001", self.TODAY)]

    def test_patient_not_found(self):

        console = FakeConsole(["1", "1", "D999"])
        query_handler = self.__query_handler(console, FakeDatabase([]))

        result = query_handler.handle(
            self.TODAY
        )

        print("\nSCENARIO: Patient Does Not Exist")
        print("Queue: D999")
        print("Expected: Patient not found message")
        print("Actual:", result)

        assert result == constants.PATIENT_NOT_FOUND_MESSAGE

    def test_current_patient_uses_today(self, monkeypatch):

        console = FakeConsole(["1", "2"])
        database = FakeDatabase([])
        io = AppTestFactory.create_io(console)
        data = DataManagerFactory.create(database)
        current_patient_query = CurrentPatientQuery(data, AppTestFactory.create_query_handler(io, data))

        monkeypatch.setattr(
            data,
            "get_current_date",
            lambda: self.TODAY
        )

        current_patient_query.run()

        print("\nSCENARIO: Current Patient")
        print("Expected Date:", self.TODAY)
        print("Actual:", database.fetched_parameters)

        assert database.fetched_parameters == [(self.TODAY,)]

    def test_past_patient_uses_selected_date(self, monkeypatch):

        console = FakeConsole(["2026-10-10", "1", "2"])
        database = FakeDatabase([])
        io = AppTestFactory.create_io(console)
        data = DataManagerFactory.create(database)
        past_patient_query = PastPatientQuery(io, AppTestFactory.create_query_handler(io, data))

        monkeypatch.setattr(
            data,
            "get_current_date",
            lambda: self.TODAY
        )

        past_patient_query.run()

        print("\nSCENARIO: Past Patient Query")
        print("Selected Date: 2026-10-10")
        print("Expected Date Used: 2026-10-10")
        print("Actual:", database.fetched_parameters)

        assert database.fetched_parameters == [("2026-10-10",)]

    def test_patient_query_database_down(self):

        # The database returns None when it cannot be reached.
        console = FakeConsole(["1", "1", "D001"])
        query_handler = self.__query_handler(console, FakeDatabase(None))

        result = query_handler.handle(
            self.TODAY
        )

        print("\nSCENARIO: Database Cannot Be Reached")
        print("Expected: Database error message")
        print("Actual:", result)

        assert result == constants.DATABASE_ERROR_MESSAGE

    def test_all_patients_on_date(self):

        console = FakeConsole(["1", "2"])
        database = FakeDatabase([
            ("09:00:00", "D001", "NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111"),
            ("09:30:00", "P001", "ALEX", "S0012345B", "M", "2001-01-01", 25, "+65 91234567")
        ])
        query_handler = self.__query_handler(console, database)

        result = query_handler.handle(
            self.TODAY
        )

        print("\nSCENARIO: All Patients On A Date")
        print("Expected: Both patients printed, no error")
        print("Actual:", result)
        print(console.shown[-1])

        assert result is None
        assert database.fetched_parameters == [(self.TODAY,)]
        assert "NANI" in console.shown[-1]
        assert "ALEX" in console.shown[-1]

    def test_all_patients_none_on_date(self):

        console = FakeConsole(["1", "2"])
        query_handler = self.__query_handler(console, FakeDatabase([]))

        result = query_handler.handle(
            self.TODAY
        )

        print("\nSCENARIO: No Patients On The Date")
        print("Expected: No records message")
        print("Actual:", result)

        assert result == constants.NO_PATIENTS_ON_DATE_MESSAGE

    def test_invalid_query_scope(self):

        console = FakeConsole(["1", "3"])
        database = FakeDatabase([])
        query_handler = self.__query_handler(console, database)

        result = query_handler.handle(
            self.TODAY
        )

        expected = io_constants.INVALID_MENU_OPTION.format(maximum=self.SCOPE_OPTIONS)

        print("\nSCENARIO: Invalid One Patient / All Patients Option")
        print("Expected:", expected)
        print("Actual:", console.shown[-1])

        assert result is None
        assert console.shown[-1] == expected
        assert database.fetched == []
