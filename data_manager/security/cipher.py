from abc import ABC, abstractmethod

class Cipher(ABC):
    """
    Interface for turning a text value into ciphertext and back again.
    Keeps the encryption lib import isolated from the other files.
    The exact encryption libraries are only used by the separate subclasses,
    allowing for different algorithms to be implemented as a new subclass.
    An example use case is utilising more complex encryption libraries, 
    for more sensitive data.
    """

    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypts inputted text. Raises ValueError if the value cannot be decrypted."""

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """Return the original text. Raise ValueError if the value cannot be decrypted."""
