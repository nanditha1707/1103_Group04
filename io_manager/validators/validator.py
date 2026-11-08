from abc import ABC, abstractmethod


class Validator(ABC):
    """Interface for checking user answers / inputs.

    Every validator inherits from this class and implements validate() 
    with its own check. Code that reads and checks user input only needs
    to know about Validator, not the specific subclass, so any validator
    can be used in its place.

    validate method returns None when user input is valid, and the 
    error message string when user input is invalid for the question. 
    """

    @abstractmethod
    def validate(self, answer: str) -> str | None:
        """Return None if the answer is valid, else the error message."""
