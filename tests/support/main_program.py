from collections.abc import Callable
from pathlib import Path

from data_manager import DataManager, DataManagerFactory
from data_manager.storage import Database
from io_manager import IOManager
from io_manager.console import Console

from .main_loader import MainLoader


class MainProgram:
    MAIN_PATH = Path(__file__).resolve().parent.parent.parent / "main.py"

    def __init__(
        self, console: Console, database: Database
    ) -> None:
        self.__io = IOManager(console, symptom_terms=[])
        self.__data = DataManagerFactory.create(database)
        self.__namespace = MainLoader(self.MAIN_PATH).load()
        self.__namespace["io"] = self.__io
        self.__namespace["data"] = self.__data

    @property
    def io(self) -> IOManager:
        return self.__io

    @property
    def data(self) -> DataManager:
        return self.__data

    def constant(self, name: str) -> object:
        return self.__namespace[name]

    def replace_function(self, name: str, replacement: Callable) -> None:
        self.__namespace[name] = replacement

    def main_menu(self) -> dict | int | None:
        return self.__namespace["main_menu"]()

    def healthcare_portal_routing(self, option: str) -> None:
        return self.__namespace["healthcare_portal_routing"](option)

    def patient_query_handler(self, date: str) -> str | None:
        return self.__namespace["patient_query_handler"](date)
