import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fakes import FakeConsole, FakeDatabase
from support import MainProgram


class TestMainMenu:
    def __start(self, console):
        return MainProgram(console, FakeDatabase([]))

    def test_successful_patient_registration(self, monkeypatch):

        patient = {
            "consent": "Y",
            "name": "NANI",
            "gender": "F",
            "age": "20",
            "current_symptoms": ["COUGH"]
        }

        console = FakeConsole([
            "1"
        ])
        program = self.__start(console)

        monkeypatch.setattr(
            program.io,
            "collect_registration",
            lambda: patient
        )

        result = program.main_menu()

        print("\nSCENARIO: Successful Registration Through Main")
        print("Expected: Patient information returned")
        print("Actual:")
        print(result)

        assert result == patient

    def test_invalid_main_menu_option(self):

        console = FakeConsole([
            "5"
        ])
        program = self.__start(console)

        result = program.main_menu()

        print("\nSCENARIO: Invalid Main Menu")
        print("Input: 5")
        print("Expected: This is not a valid option!")
        print("Actual:", console.shown[-1])

        assert result is None
        assert console.shown[-1] == "This is not a valid option!"

    def test_healthcare_portal_selected(self):

        console = FakeConsole([
            "2",    # Main menu
            "1"     # Current patient query
        ])
        program = self.__start(console)

        selected = []

        program.replace_function(
            "healthcare_portal_routing",
            lambda option: selected.append(option)
        )

        program.main_menu()

        print("\nSCENARIO: Healthcare Portal Selected")
        print("Expected Portal Option: 1")
        print("Actual:", selected)

        assert selected == ["1"]

    def test_correct_exit_password(self):

        console = FakeConsole([
            "3",
            "Password"
        ])
        program = self.__start(console)

        result = program.main_menu()

        print("\nSCENARIO: Correct Exit Password")
        print("Expected:", program.constant("QUIT_SIGNAL"))
        print("Actual:", result)

        assert result == program.constant("QUIT_SIGNAL")
        assert console.shown[-1] == program.constant("MENU_EXIT_MESSAGE")

    def test_wrong_exit_password(self):

        console = FakeConsole([
            "3",
            "WRONG"
        ])
        program = self.__start(console)

        result = program.main_menu()

        print("\nSCENARIO: Wrong Exit Password")
        print("Expected: This is not the right password!")
        print("Actual:", console.shown[-1])

        assert result is None
        assert console.shown[-1] == "This is not the right password!"
