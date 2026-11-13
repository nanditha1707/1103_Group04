import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import DataManagerFactory
from fakes import FakeConsole, FakeDatabase
from io_manager import IOManager
from main_loader import load_main


main = load_main()


def use_fakes(monkeypatch, inputs, rows):

    console = FakeConsole(inputs)
    database = FakeDatabase(rows)

    monkeypatch.setitem(
        main,
        "io",
        IOManager(console, symptom_terms=[])
    )

    monkeypatch.setitem(
        main,
        "data",
        DataManagerFactory.create(database)
    )

    return console, database


def test_current_patient_found(monkeypatch):

    console, database = use_fakes(
        monkeypatch,
        ["1", "1", "D001"],
        [
            ("NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111")
        ]
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: Existing Patient Query")
    print("Queue: D001")
    print("Expected Patient: NANI")
    print("Actual:")
    print(console.shown[-1])

    assert result is None
    assert "NANI" in console.shown[-1]
    assert "T0111111C" in console.shown[-1]
    assert database.fetched_parameters == [("D001", "2026-10-14")]


def test_patient_not_found(monkeypatch):

    use_fakes(
        monkeypatch,
        ["1", "1", "D999"],
        []
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: Patient Does Not Exist")
    print("Queue: D999")
    print("Expected: Patient not found message")
    print("Actual:", result)

    assert result == (
        "There is no such patient, "
        "please enter a valid queue number!"
    )


def test_current_patient_uses_today(monkeypatch):

    dates = []

    use_fakes(monkeypatch, [], [])

    monkeypatch.setattr(
        main["data"],
        "get_current_date",
        lambda: "2026-10-14"
    )

    monkeypatch.setitem(
        main,
        "patient_query_handler",
        lambda date: dates.append(date)
    )

    main["healthcare_portal_routing"]("1")

    print("\nSCENARIO: Current Patient")
    print("Expected Date: 2026-10-14")
    print("Actual:", dates)

    assert dates == ["2026-10-14"]


def test_past_patient_uses_selected_date(monkeypatch):

    dates = []

    use_fakes(
        monkeypatch,
        ["2026-10-10"],
        []
    )

    monkeypatch.setattr(
        main["data"],
        "get_current_date",
        lambda: "2026-10-14"
    )

    monkeypatch.setitem(
        main,
        "patient_query_handler",
        lambda date: dates.append(date)
    )

    main["healthcare_portal_routing"]("2")

    print("\nSCENARIO: Past Patient Query")
    print("Selected Date: 2026-10-10")
    print("Expected Date Used: 2026-10-10")
    print("Actual:", dates)

    assert dates == ["2026-10-10"]


def test_patient_query_database_down(monkeypatch):

    # The database returns None when it cannot be reached.
    use_fakes(
        monkeypatch,
        ["1", "1", "D001"],
        None
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: Database Cannot Be Reached")
    print("Expected: Database error message")
    print("Actual:", result)

    assert result == main["DATABASE_ERROR_MESSAGE"]


def test_all_patients_on_date(monkeypatch):

    console, database = use_fakes(
        monkeypatch,
        ["1", "2"],
        [
            ("09:00:00", "D001", "NANI", "T0111111C", "F", "2006-01-01", 20, "+65 91111111"),
            ("09:30:00", "P001", "ALEX", "S0012345B", "M", "2001-01-01", 25, "+65 91234567")
        ]
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: All Patients On A Date")
    print("Expected: Both patients printed, no error")
    print("Actual:", result)
    print(console.shown[-1])

    assert result is None
    assert database.fetched_parameters == [("2026-10-14",)]
    assert "NANI" in console.shown[-1]
    assert "ALEX" in console.shown[-1]


def test_all_patients_none_on_date(monkeypatch):

    use_fakes(
        monkeypatch,
        ["1", "2"],
        []
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: No Patients On The Date")
    print("Expected: No records message")
    print("Actual:", result)

    assert result == "There are no patient records for this date!"


def test_invalid_query_scope(monkeypatch):

    use_fakes(
        monkeypatch,
        ["1", "3"],
        []
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: Invalid One Patient / All Patients Option")
    print("Expected: Invalid option message")
    print("Actual:", result)

    assert result == "This is not a valid option number!"
