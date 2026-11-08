import json
from typing import Callable

import pandas as pd


class AiOutput:
    """Parses, formats and validates the AI's output against the cleaned
    ICD-11 and HSA datasets."""

    def __init__(
        self,
        icd_df: pd.DataFrame | None,
        hsa_df: pd.DataFrame | None,
        classify_medicine: Callable[[str, pd.DataFrame], str | None],
        explanation_fields: list[str]
    ):
        self.__icd_df = icd_df
        self.__hsa_df = hsa_df
        # Looks up a medicine's HSA classification (logic.get_classification),
        # None if not found.
        self.__classify_medicine = classify_medicine
        # The 2 explanation fields, which are not stripped or uppercased.
        self.__explanation_fields = explanation_fields

    @staticmethod
    def parse(text: str) -> dict:
        """Parse the AI's JSON text output into a Python dictionary."""
        return json.loads(text)

    def format(self, ai_output: dict) -> dict:
        """Strip and uppercase every string field in the AI output except the
        2 explanations.

        Stripping turns blank emergency medicines (' ') into empty strings.
        Non string fields like ai_confidence_score are left unchanged.
        """
        # For each field in AI output.
        for key, value in ai_output.items():
            # If the field is not an explanation field and is of type string,
            # then remove spaces at the start and end and uppercase them.
            if key not in self.__explanation_fields and isinstance(value, str):
                ai_output[key] = value.strip().upper()

        return ai_output        