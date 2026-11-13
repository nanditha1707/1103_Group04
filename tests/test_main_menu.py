import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fakes import FakeConsole
from io_manager import IOManager
from main_loader import load_main


main = load_main()


def use_console(monkeypatch, inputs):

    console = FakeConsole(inputs)
    io = IOManager(console, symptom_terms=[])

    monkeypatch.setitem(
        main,
        "io",
        io
    )

    return io, console


def test_successful_patient_registration(monkeypatch):

    patient = {
        "consent": "Y",
        "name": "NANI",
        "gender": "F",
        "age": "20",
        "current_symptoms": ["COUGH"]
    }

    io, console = use_console(monkeypatch, [
        "1"
    ])

    monkeypatch.setattr(
        io,
        "collect_registration",
        lambda: patient
    )

    result = main["main_menu"]()

    print("\nSCENARIO: Successful Registration Through Main")
    print("Expected: Patient information returned")
    print("Actual:")
    print(result)

    assert result == patient


def test_invalid_main_menu_option(monkeypatch):

    io, console = use_console(monkeypatch, [
        "5"
    ])

    result = main["main_menu"]()

    print("\nSCENARIO: Invalid Main Menu")
    print("Input: 5")
    print("Expected: This is not a valid option!")
    print("Actual:", console.shown[-1])

    assert result is None
    assert console.shown[-1] == "This is not a valid option!"


def test_healthcare_portal_selected(monkeypatch):

    io, console = use_console(monkeypatch, [
        "2",    # Main menu
        "1"     # Current patient query
    ])

    selected = []

    monkeypatch.setitem(
        main,
        "healthcare_portal_routing",
        lambda option: selected.append(option)
    )

    main["main_menu"]()

    print("\nSCENARIO: Healthcare Portal Selected")
    print("Expected Portal Option: 1")
    print("Actual:", selected)

    assert selected == ["1"]


def test_correct_exit_password(monkeypatch):

    io, console = use_console(monkeypatch, [
        "3",
        "Password"
    ])

    result = main["main_menu"]()

    print("\nSCENARIO: Correct Exit Password")
    print("Expected:", main["QUIT_SIGNAL"])
    print("Actual:", result)

    assert result == main["QUIT_SIGNAL"]
    assert console.shown[-1] == main["MENU_EXIT_MESSAGE"]


def test_wrong_exit_password(monkeypatch):

    io, console = use_console(monkeypatch, [
        "3",
        "WRONG"
    ])

    result = main["main_menu"]()

    print("\nSCENARIO: Wrong Exit Password")
    print("Expected: This is not the right password!")
    print("Actual:", console.shown[-1])

    assert result is None
    assert console.shown[-1] == "This is not the right password!"
