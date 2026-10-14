import ast
from pathlib import Path


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


def test_successful_patient_registration(monkeypatch):

    patient = {
        "consent": "Y",
        "name": "NANI",
        "gender": "F",
        "age": "20",
        "current_symptoms": ["COUGH"]
    }

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "1"
    )

    monkeypatch.setattr(
        main["io"],
        "run_questions",
        lambda: patient
    )

    monkeypatch.setattr(
        main["io"],
        "confirm_inputs",
        lambda answers: True
    )

    result = main["main_menu"]()

    print("\nSCENARIO: Successful Registration Through Main")
    print("Expected: Patient information returned")
    print("Actual:")
    print(result)

    assert result == patient


def test_invalid_main_menu_option(monkeypatch):

    messages = []

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "5"
    )

    monkeypatch.setattr(
        main["io"],
        "print_message",
        lambda message: messages.append(message)
    )

    main["main_menu"]()

    print("\nSCENARIO: Invalid Main Menu")
    print("Input: 5")
    print("Expected: This is not a valid option!")
    print("Actual:", messages)

    assert "This is not a valid option!" in messages


def test_healthcare_portal_selected(monkeypatch):

    choices = iter([
        "2",    # Main menu
        "1"     # Current patient query
    ])

    selected = []

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: next(choices)
    )

    monkeypatch.setattr(
        main["io"],
        "validate_option",
        lambda option: None
    )

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

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "3"
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "Password"
    )

    monkeypatch.setattr(
        main["io"],
        "print_message",
        lambda message: None
    )

    result = main["main_menu"]()

    print("\nSCENARIO: Correct Exit Password")
    print("Expected:", main["io"].QUIT_SIGNAL)
    print("Actual:", result)

    assert result == main["io"].QUIT_SIGNAL


def test_wrong_exit_password(monkeypatch):

    messages = []

    monkeypatch.setattr(
        main["io"],
        "dynamic_menu_print",
        lambda *args: "3"
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "WRONG"
    )

    monkeypatch.setattr(
        main["io"],
        "print_message",
        lambda message: messages.append(message)
    )

    result = main["main_menu"]()

    print("\nSCENARIO: Wrong Exit Password")
    print("Expected: This is not the right password!")
    print("Actual:", messages)

    assert result is None
    assert "This is not the right password!" in messages