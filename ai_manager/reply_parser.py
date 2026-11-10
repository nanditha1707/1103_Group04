import json
from collections.abc import Collection

from .constants import EXPLANATION_FIELDS


class ReplyParser:
    def __init__(self, free_text_fields: Collection[str] = EXPLANATION_FIELDS):
        self.__free_text_fields = free_text_fields

    def parse(self, reply: str) -> dict:
        output = json.loads(reply)

        return {
            key: self.__normalise(key, value)
            for key, value in output.items()
        }

    def __normalise(self, key: str, value: object) -> object:
        if key in self.__free_text_fields or not isinstance(value, str):
            return value

        return value.strip().upper()
