import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import constants
from app_test_factory import AppTestFactory
from fakes import FakeConsole, FakeDatabase, FakeDiagnoser
from io_manager import constants as io_constants


class TestMainMenu:
    TODAY = "2026-10-14"
    MAIN_MENU_OPTIONS = 3

    def __clock(self):
        return datetime.fromisoformat(self.TODAY)

    def test_successful_patient_registration(self, monkeypatch):

        patient = {
            "consent": "Y",
            "name": "NANI",
            "nric": "T0111111C",
            "gender": "F",
            "birthdate": "2006-01-01",
            "age": "20",
            "phone_number": "+65 91111111",
            "pregnancy": "N",
            "current_symptoms": ["COUGH"],
            "symptom_onset_days": "2",
            "chronic_conditions": "N",
            "current_medications": "N",
            "drug_allergies": "N"
        }

        ai_output = {
            "primary_diagnosis_ICD11_Code": "CA00",
            "primary_diagnosis_ICD11_Title": "Common Cold",
            "primary_diagnosis_explanation": "Cold symptoms",
            "primary_diagnosis_medicine_1": "PARACETAMOL",
            "primary_diagnosis_medicine_2": None,
            "secondary_diagnosis_ICD11_Code": None,
            "secondary_diagnosis_ICD11_Title": None,
            "secondary_diagnosis_explanation": None,
            "secondary_diagnosis_medicine_1": None,
            "secondary_diagnosis_medicine_2": None,
            "ai_confidence_score": 90
        }

        console = FakeConsole([
            "1"
        ])
        database = FakeDatabase([(None,)])
        diagnoser = FakeDiagnoser(ai_output)
        io = AppTestFactory.create_io(console)
        data = AppTestFactory.create_data_manager(database)
        main_menu = AppTestFactory.create_main_menu(io, data, diagnoser)

        monkeypatch.setattr(
            io,
            "collect_registration",
            lambda: patient
        )

        keep_running = main_menu.run_once()

        saved_record = database.executed[0][1]

        print("\nSCENARIO: Successful Registration Through Main")
        print("Expected: Patient record saved, personal details kept from the AI")
        print("Sent to AI:", diagnoser.received)
        print("Saved:")
        print(saved_record)

        assert keep_running is True
        assert len(diagnoser.received) == 1
        assert "name" not in diagnoser.received[0]
        assert "nric" not in diagnoser.received[0]
        assert len(database.executed) == 1
        assert saved_record["name"] == "NANI"
        assert saved_record["current_symptoms"] == "COUGH"
        assert saved_record["primary_diagnosis_ICD11_Code"] == "CA00"
        assert saved_record["route"] == "Doctor"
        assert saved_record["queue_number"] == "D001"
        assert "D001" in console.shown[-1]

    def test_invalid_main_menu_option(self):

        console = FakeConsole([
            "5"
        ])
        io = AppTestFactory.create_io(console)
        data = AppTestFactory.create_data_manager(FakeDatabase([]))
        main_menu = AppTestFactory.create_main_menu(io, data)

        keep_running = main_menu.run_once()

        expected = io_constants.INVALID_MENU_OPTION.format(maximum=self.MAIN_MENU_OPTIONS)

        print("\nSCENARIO: Invalid Main Menu")
        print("Input: 5")
        print("Expected:", expected)
        print("Actual:", console.shown[-1])

        assert keep_running is True
        assert console.shown[-1] == expected

    def test_healthcare_portal_selected(self):

        console = FakeConsole([
            "2",    # Main menu
            "1",    # Current patient query
            "1",
            "2"
        ])
        database = FakeDatabase([])
        io = AppTestFactory.create_io(console)
        data = AppTestFactory.create_data_manager(database, self.__clock)
        main_menu = AppTestFactory.create_main_menu(io, data)

        keep_running = main_menu.run_once()

        print("\nSCENARIO: Healthcare Portal Selected")
        print("Expected Query Date:", self.TODAY)
        print("Actual:", database.fetched_parameters)

        assert keep_running is True
        assert database.fetched_parameters == [(self.TODAY,)]
        assert console.shown[-1] == constants.NO_PATIENTS_ON_DATE_MESSAGE

    def test_correct_exit_password(self):

        console = FakeConsole([
            "3",
            "Password"
        ])
        io = AppTestFactory.create_io(console)
        data = AppTestFactory.create_data_manager(FakeDatabase([]))
        main_menu = AppTestFactory.create_main_menu(io, data)

        keep_running = main_menu.run_once()

        print("\nSCENARIO: Correct Exit Password")
        print("Expected:", constants.MENU_EXIT_MESSAGE)
        print("Actual:", console.shown[-1])

        assert keep_running is False
        assert console.shown[-1] == constants.MENU_EXIT_MESSAGE

    def test_wrong_exit_password(self):

        console = FakeConsole([
            "3",
            "WRONG"
        ])
        io = AppTestFactory.create_io(console)
        data = AppTestFactory.create_data_manager(FakeDatabase([]))
        main_menu = AppTestFactory.create_main_menu(io, data)

        keep_running = main_menu.run_once()

        print("\nSCENARIO: Wrong Exit Password")
        print("Expected:", constants.WRONG_PASSWORD_MESSAGE)
        print("Actual:", console.shown[-1])

        assert keep_running is True
        assert console.shown[-1] == constants.WRONG_PASSWORD_MESSAGE
