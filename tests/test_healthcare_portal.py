import ast
from pathlib import Path

import pandas as pd


def load_main():

    main_path = Path(__file__).resolve().parent.parent / "main.py"

    source = main_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    safe_nodes = []

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
                ast.Assign,
                ast.AnnAssign,
                ast.FunctionDef
            )
        ):
            safe_nodes.append(node)

    safe_tree = ast.Module(
        body=safe_nodes,
        type_ignores=[]
    )

    namespace = {}

    exec(
        compile(
            safe_tree,
            str(main_path),
            "exec"
        ),
        namespace
    )

    return namespace


main = load_main()


def test_current_patient_found(monkeypatch):

    fake_patient = pd.DataFrame([
        {
            "name": "NANI",
            "nric": "T0111111C",
            "gender": "F",
            "age": "20",
            "phone_number": "+65 91111111"
        }
    ])

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "1"
    )

    monkeypatch.setattr(
        main["io"],
        "validate_option",
        lambda option: None
    )

    monkeypatch.setattr(
        main["data"],
        "get_patient_filter",
        lambda option: [
            "name",
            "nric",
            "gender",
            "age",
            "phone_number"
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "D001"
    )

    monkeypatch.setattr(
        main["data"],
        "load_records",
        lambda: pd.DataFrame()
    )

    monkeypatch.setattr(
        main["data"],
        "get_patient_by_queue",
        lambda records, queue, filters, date: fake_patient
    )

    printed = []

    monkeypatch.setattr(
        main["io"],
        "print_df",
        lambda df: printed.append(df)
    )

    result = main["patient_query_handler"](
        "2026-10-14"
    )

    print("\nSCENARIO: Existing Patient Query")
    print("Queue: D001")
    print("Expected Patient: NANI")
    print("Actual:")
    print(fake_patient)

    assert result is None
    assert len(printed) == 1


def test_patient_not_found(monkeypatch):

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "1"
    )

    monkeypatch.setattr(
        main["io"],
        "validate_option",
        lambda option: None
    )

    monkeypatch.setattr(
        main["data"],
        "get_patient_filter",
        lambda option: ["name"]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "D999"
    )

    monkeypatch.setattr(
        main["data"],
        "load_records",
        lambda: pd.DataFrame()
    )

    monkeypatch.setattr(
        main["data"],
        "get_patient_by_queue",
        lambda records, queue, filters, date: None
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

    monkeypatch.setattr(
        main["data"],
        "get_current_date",
        lambda: "2026-10-14"
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "2026-10-10"
    )

    monkeypatch.setattr(
        main["io"],
        "validate_date",
        lambda date: None
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