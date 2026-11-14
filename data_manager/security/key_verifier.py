from .cipher import Cipher
from .key_check_store import KeyCheckStore

class KeyVerifier:
    """
    Checks at startup that the cipher's key,
    matches the key the database was encrypted with, by decrypting a known value check.
    """

    def __init__(
        self, cipher: Cipher, check_store: KeyCheckStore, check_text: str
    ):
        self.__cipher = cipher
        self.__check_store = check_store
        self.__check_text = check_text

    def verify(self) -> str | None:
        """
        Return None if the key is correct, or the error message if the database
        could not be reached, has no check value, or the key does not match.
        """
        check_values = self.__check_store.get_check_values()
        if check_values is None:
            return "The database could not be reached to check the encryption key."

        if not check_values:
            return "The database has no encryption check value to verify the key against."

        return self.__check_value_matches(check_values[0])

    def __check_value_matches(self, check_value: str) -> str | None:
        try:
            decrypted_text = self.__cipher.decrypt(check_value)
        except ValueError:
            # In the scenario where the key is invalid, it changes the text to None.
            decrypted_text = None

        # Wraps both the wrong key possibility, 
        # and invalid key possibility into one error message.
        if decrypted_text != self.__check_text:
            return ("The encryption key does not match this database." 
                    "Either the key is invalid, or it is meant for different database.")
        
