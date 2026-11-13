import ast
from pathlib import Path


class MainLoader:
    _DEFINITIONS = (ast.Import, ast.ImportFrom, ast.FunctionDef)
    _ASSIGNMENTS = (ast.Assign, ast.AnnAssign)

    def __init__(
        self, main_path: Path
    ) -> None:
        self.__main_path = main_path

    def load(self) -> dict:
        source = self.__main_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        safe_nodes = []

        for node in tree.body:
            if self.__is_safe(node):
                safe_nodes.append(node)

        safe_tree = ast.Module(
            body=safe_nodes,
            type_ignores=[]
        )

        namespace = {}

        exec(
            compile(
                safe_tree,
                str(self.__main_path),
                "exec"
            ),
            namespace
        )

        return namespace

    def __is_safe(self, node: ast.AST) -> bool:
        if isinstance(node, self._DEFINITIONS):
            return True

        if isinstance(node, self._ASSIGNMENTS):
            return not self.__builds_an_object(node)

        return False

    @staticmethod
    def __builds_an_object(node: ast.AST) -> bool:
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                return True

        return False
