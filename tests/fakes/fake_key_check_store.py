from typing import override

from data_manager import constants
from data_manager.security import KeyCheckStore


class FakeKeyCheckStore(KeyCheckStore):
    """Holds the check text as FakeCipher would encrypt it (unchanged), so the
    key check always passes without adding calls to FakeDatabase."""

    @override
    def get_check_values(self) -> list[str] | None:
        return [constants.KEY_CHECK_TEXT]
