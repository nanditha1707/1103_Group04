from typing import override

from data_manager import constants
from data_manager.security import KeyCheckStore


class FakeKeyCheckStore(KeyCheckStore):
    """By default holds the check text as FakeCipher would encrypt it
    (unchanged), so the key check always passes without adding calls to
    FakeDatabase. Pass other check values to test KeyVerifier, or None to
    act as a database that could not be reached."""

    def __init__(
        self, check_values: tuple[str, ...] | None = (constants.KEY_CHECK_TEXT,)
    ):
        self.__check_values = check_values

    @override
    def get_check_values(self) -> list[str] | None:
        if self.__check_values is None:
            return None
        return list(self.__check_values)
