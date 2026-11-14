from typing import override

from data_manager.security import Cipher


class FakeCipher(Cipher):
    """Leaves every value unchanged, so tests can give FakeDatabase plain
    rows and check the saved values directly."""

    @override
    def encrypt(self, plaintext: str) -> str:
        return plaintext

    @override
    def decrypt(self, ciphertext: str) -> str:
        return ciphertext
