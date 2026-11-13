import sys
from datetime import date, datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fakes import FakeConsole
from io_manager import IOManager, constants
from io_manager.form import RegistrationFactory


class TestRegistration:
    CONFIRM_ALL_INPUTS = "17"
    MINIMUM_AGE = RegistrationFactory.MINIMUM_SELF_REGISTRATION_AGE
    SYMPTOM_TERMS = ("SORE THROAT",)

    def __register(self, console):
        io = IOManager(console, symptom_terms=self.SYMPTOM_TERMS)

        return io.collect_registration()

    @staticmethod
    def __birthdate_for_age(age):
        today = datetime.now(RegistrationFactory.TIMEZONE).date()

        return date(today.year - age, 1, 1).isoformat()

    def test_normal_female_registration(self):

        # Automatically answers every registration question.
        console = FakeConsole([
            "Y",                            # Consent
            "NANI",                         # Name
            "T0111111C",                    # NRIC
            "F",                            # Gender
            self.__birthdate_for_age(20),   # Birthdate
            "+65 91111111",                 # Phone
            "N",                            # Pregnant
            "N",                            # Chest pain
            "N",                            # Breathing difficulties
            "N",                            # Signs of stroke
            "N",                            # Self-harm
            "1",                            # Symptom: Cough
            "7",                            # Done adding symptoms
            "2",                            # Symptoms started 2 days ago
            "N",                            # Chronic conditions
            "N",                            # Current medication
            "N",                            # Drug allergies
            self.CONFIRM_ALL_INPUTS
        ])

        result = self.__register(console)

        print("\nSCENARIO: Normal Female Registration")
        print("Expected: Registration completes")
        print("Expected Gender: F")
        print("Expected Age: 20")
        print("Expected Pregnancy: N")
        print("Expected Symptoms: ['COUGH']")
        print("Actual:")
        print(result)

        assert result is not None
        assert result["name"] == "NANI"
        assert result["gender"] == "F"
        assert result["birthdate"] == self.__birthdate_for_age(20)
        assert result["age"] == "20"
        assert result["pregnancy"] == "N"
        assert result["current_symptoms"] == ["COUGH"]
        assert console.shown[-1] == constants.CONFIRMED_MESSAGE

    def test_normal_male_registration(self):

        # The program should automatically skip pregnancy for males.
        console = FakeConsole([
            "Y",
            "ALEX TAN",
            "S0012345B",
            "M",
            self.__birthdate_for_age(25),
            "+65 91234567",
            # Pregnancy is skipped here.
            "N",                # Chest pain
            "N",                # Breathing difficulties
            "N",                # Signs of stroke
            "N",                # Self-harm
            "2",                # Flu
            "7",                # Done
            "3",                # 3 days
            "N",
            "N",
            "N",
            self.CONFIRM_ALL_INPUTS
        ])

        result = self.__register(console)

        print("\nSCENARIO: Normal Male Registration")
        print("Expected: Pregnancy question skipped")
        print("Expected Pregnancy Value: None")
        print("Actual:")
        print(result)

        assert result is not None
        assert result["gender"] == "M"
        assert result["pregnancy"] is None
        assert result["current_symptoms"] == ["FLU"]
        assert constants.PREGNANCY_PROMPT not in console.prompts

    def test_no_consent(self):

        console = FakeConsole([
            "N"
        ])

        result = self.__register(console)

        print("\nSCENARIO: Patient Does Not Consent")
        print("Expected: Registration stops")
        print("Actual:", result)

        assert result is None
        assert console.shown[-1] == constants.REG_EXIT_MESSAGE

    def test_emergency_chest_pain(self):

        console = FakeConsole([
            "Y",
            "CHARLIE NG",
            "S8812345C",
            "M",
            self.__birthdate_for_age(58),
            "+65 92345678",

            # Pregnancy skipped.

            "Y"                 # Chest pain
        ])

        result = self.__register(console)

        print("\nSCENARIO: Emergency Chest Pain")
        print("Chest Pain: Y")
        print("Expected: Registration stops and patient is sent to nurse")
        print("Actual:", result)

        assert result is None
        assert console.shown[-1] == constants.NURSE_ALERT_MESSAGE

    def test_underage_patient(self):

        console = FakeConsole([
            "Y",
            "JANE TAN",
            "T1111111A",
            "F",
            self.__birthdate_for_age(self.MINIMUM_AGE - 1)      # Birthdate
        ])

        result = self.__register(console)

        print("\nSCENARIO: Underage Patient")
        print("Age:", self.MINIMUM_AGE - 1)
        print("Expected: Registration stops and patient is sent to manual registration")
        print("Actual:", result)

        assert result is None
        assert console.shown[-1] == constants.UNDERAGE_MESSAGE.format(minimum=self.MINIMUM_AGE)
