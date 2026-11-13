from cryptography.fernet import Fernet, InvalidToken

from .cipher import Cipher


class FernetCipher(Cipher):
    """Encrypts text with Fernet, using a key read from the .env file."""

    def __init__(
        self, key: str | None
    ):
        # If the decryption key is missing,
        # It raises a ValueError and closes the program.
        if not key:
            raise ValueError("No encryption key was given")

        # Fernet raises ValueError itself if the key is malformed.
        self.__fernet = Fernet(key.encode("utf-8"))

    def encrypt(self, plaintext: str) -> str:
        token = self.__fernet.encrypt(plaintext.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        try:
            plaintext = self.__fernet.decrypt(ciphertext.encode("utf-8"))
        except InvalidToken as error:
            # Replace the default error from fernet with a custom error message.
            raise ValueError("The value could not be decrypted") from error

        return plaintext.decode("utf-8")
