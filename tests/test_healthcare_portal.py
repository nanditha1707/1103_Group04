import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fakes import FakeConsole, FakeDatabase
from support import MainProgram


class TestHealthcarePortal:
    TODAY = "2026-10-14"

    def test_current_patient_found(self):

        console = FakeConsole(["1", "1", "D001"])
        database = FakeDatabase([
            ("NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111")
        ])
        program = MainProgram(console, database)

        result = program.patient_query_handler(
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
        program = MainProgram(console, FakeDatabase([]))

        result = program.patient_query_handler(
            self.TODAY
        )

        print("\nSCENARIO: Patient Does Not Exist")
        print("Queue: D999")
        print("Expected: Patient not found message")
        print("Actual:", result)

        assert result == (
            "There is no such patient, "
            "please enter a valid queue number!"
        )

    def test_current_patient_uses_today(self, monkeypatch):

        dates = []

        program = MainProgram(FakeConsole(), FakeDatabase([]))

        monkeypatch.setattr(
            program.data,
            "get_current_date",
            lambda: self.TODAY
        )

        program.replace_function(
            "patient_query_handler",
            lambda date: dates.append(date)
        )

        program.healthcare_portal_routing("1")

        print("\nSCENARIO: Current Patient")
        print("Expected Date:", self.TODAY)
        print("Actual:", dates)

        assert dates == [self.TODAY]

    def test_past_patient_uses_selected_date(self, monkeypatch):

        dates = []

        program = MainProgram(FakeConsole(["2026-10-10"]), FakeDatabase([]))

        monkeypatch.setattr(
            program.data,
            "get_current_date",
            lambda: self.TODAY
        )

        program.replace_function(
            "patient_query_handler",
            lambda date: dates.append(date)
        )

        program.healthcare_portal_routing("2")

        print("\nSCENARIO: Past Patient Query")
        print("Selected Date: 2026-10-10")
        print("Expected Date Used: 2026-10-10")
        print("Actual:", dates)

        assert dates == ["2026-10-10"]

    def test_patient_query_database_down(self):

        # The database returns None when it cannot be reached.
        console = FakeConsole(["1", "1", "D001"])
        program = MainProgram(console, FakeDatabase(None))

        result = program.patient_query_handler(
            self.TODAY
        )

        print("\nSCENARIO: Database Cannot Be Reached")
        print("Expected: Database error message")
        print("Actual:", result)

        assert result == program.constant("DATABASE_ERROR_MESSAGE")

    def test_all_patients_on_date(self):

        console = FakeConsole(["1", "2"])
        database = FakeDatabase([
            ("09:00:00", "D001", "NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111"),
            ("09:30:00", "P001", "ALEX", "S0012345B", "M", "2001-01-01", 25, "+65 91234567")
        ])
        program = MainProgram(console, database)

        result = program.patient_query_handler(
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
        program = MainProgram(console, FakeDatabase([]))

        result = program.patient_query_handler(
            self.TODAY
        )

        print("\nSCENARIO: No Patients On The Date")
        print("Expected: No records message")
        print("Actual:", result)

        assert result == "There are no patient records for this date!"

    def test_invalid_query_scope(self):

        console = FakeConsole(["1", "3"])
        program = MainProgram(console, FakeDatabase([]))

        result = program.patient_query_handler(
            self.TODAY
        )

        print("\nSCENARIO: Invalid One Patient / All Patients Option")
        print("Expected: Invalid option message")
        print("Actual:", result)

        assert result == "This is not a valid option number!"
