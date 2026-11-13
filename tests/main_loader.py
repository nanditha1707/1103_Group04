import ast
from pathlib import Path


def builds_an_object(node: ast.AST) -> bool:

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            return True

    return False


def load_main() -> dict:

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
                ast.FunctionDef
            )
        ):
            safe_nodes.append(node)

        elif isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign
            )
        ) and not builds_an_object(node):
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
