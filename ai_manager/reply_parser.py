import json
from collections.abc import Collection
from ai_manager.errors import InvalidOutputError
from .constants import EXPLANATION_FIELDS


class ReplyParser:
    """Turns the AI's JSON reply into a dictionary that can be compared
    with the cleaned datasets."""

    def __init__(self, free_text_fields: Collection[str] = EXPLANATION_FIELDS):
        # Fields that hold free text, so they are not stripped and uppercased.
        self.__free_text_fields = free_text_fields

    def parse(self, reply: str) -> dict:
        """Parse the reply, then strip and uppercase every string field
        except the free text ones, to match the cleaned datasets.

        Stripping turns blank emergency medicines (' ') into empty strings.
        Non string fields like ai_confidence_score are left unchanged.
        Raises InvalidOutputError if the reply is not valid JSON.
        """
        try:
            output = json.loads(reply)
        except json.JSONDecodeError as error:
            raise InvalidOutputError("AI reply is not valid JSON") from error

        return {
            key: self.__normalise(key, value)
            for key, value in output.items()
        }

    def __normalise(self, key: str, value: object) -> object:
        """Return the value stripped and uppercased, unless it is free text
        or not a string."""
        if key in self.__free_text_fields or not isinstance(value, str):
            return value

        return value.strip().upper()
