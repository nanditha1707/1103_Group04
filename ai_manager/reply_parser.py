import json
from collections.abc import Collection, Mapping
from ai_manager.errors import InvalidOutputError
from .constants import AI_OUTPUT_FIELDS, EXPLANATION_FIELDS


class ReplyParser:
    """Turns the AI's JSON reply into a dictionary that can be compared
    with the cleaned datasets."""

    _PYTHON_TYPES = {"string": str, "integer": int}

    def __init__(
        self, free_text_fields: Collection[str] = EXPLANATION_FIELDS, output_fields: Mapping[str, dict] = AI_OUTPUT_FIELDS
    ):
        # Fields that hold free text, so they are not stripped and uppercased.
        self.__free_text_fields = free_text_fields
        self.__output_fields = output_fields

    def parse(self, reply: str) -> dict:
        """Parse the reply, then strip and uppercase every string field
        except the free text ones, to match the cleaned datasets.

        Stripping turns blank emergency medicines (' ') into empty strings.
        Non string fields like ai_confidence_score are left unchanged.
        Raises InvalidOutputError if the reply is not valid JSON or does
        not have every output field with the right type.
        """
        try:
            output = json.loads(reply)
        except json.JSONDecodeError as error:
            raise InvalidOutputError("AI reply is not valid JSON") from error

        self.__check_shape(output)

        return {
            key: self.__normalise(key, value)
            for key, value in output.items()
        }

    def __check_shape(self, output: object) -> None:
        """Raise InvalidOutputError unless the output is a JSON object
        with every output field holding a value of the right type.

        The provider schemas should already force this shape. A reply that
        gets past them would otherwise crash OutputValidator with an error
        ErrorClassifier treats as unexpected, so no other model is tried.
        """
        if not isinstance(output, dict):
            raise InvalidOutputError("AI reply is not a JSON object")

        for field, schema in self.__output_fields.items():
            if field not in output:
                raise InvalidOutputError(f"AI reply is missing {field}")

            if not self.__has_type(output[field], schema["type"]):
                raise InvalidOutputError(f"AI reply has the wrong type for {field}")

    def __has_type(self, value: object, json_type: str) -> bool:
        """Return True if the value is the Python type for the JSON schema
        type. bool is a subclass of int. True and false are rejected
        rather than passing as integers."""
        if isinstance(value, bool):
            return False

        return isinstance(value, self._PYTHON_TYPES[json_type])

    def __normalise(self, key: str, value: object) -> object:
        """Return the value stripped and uppercased, unless it is free text
        or not a string."""
        if (
            key in self.__free_text_fields
            or not isinstance(value, str)
        ):
            return value

        return value.strip().upper()
