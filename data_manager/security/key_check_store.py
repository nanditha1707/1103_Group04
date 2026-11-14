from abc import ABC, abstractmethod

class KeyCheckStore(ABC):
    """
    Interface for storing an encrypted check value in the DB, 
    to be used at startup, in order to confirm that the key in the .env,
    is the same key the database is encrypted in.
    """

    @abstractmethod
    def get_check_values(self) -> list[str] | None:
        """Returns the saved check value in a list, an empty list if none is saved,
        or None if the database could not be reached."""
