from typing import override

from data_manager.security import KeyCheckStore


class FakeKeyCheckStore(KeyCheckStore):
    """Acts like a new database with no check value saved yet, so the key
    check always passes without adding calls to FakeDatabase."""

    def __init__(
        self
    ) -> None:
        self.__saved_values: list[str] = []

    @property
    def saved_values(self) -> list[str]:
        return list(self.__saved_values)

    @override
    def get_check_values(self) -> list[str] | None:
        return []

    @override
    def save_check_value(self, check_value: str) -> str | None:
        self.__saved_values.append(check_value)
        return None
