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
       
    def validate_diagnosis(self, ai_diagnosis: str, ai_code: str) -> bool:
        """
        Check that an AI diagnosis title and its code are in the cleaned
        ICD11 dataset.

        Returns True only if the title and code are an exact match on the
        same row, so a real title paired with the wrong code fails.
        Expects the title and code to already be stripped and uppercased by
        format_ai_output, the same as the cleaned dataset.
        """

        # Creates a mask of the rows where both the disease name and the
        # code match, so they have to be on the same row.
        is_match = (
            (self.__icd_df["DiseaseName"] == ai_diagnosis)
            & (self.__icd_df["Code"] == ai_code)
        )

        return bool(is_match.any())

    def validate_medicine(self, ai_medicine: str) -> bool:
        """
        Check that an AI medicine is in the cleaned HSA dataset.

        Returns True if the medicine is found inside any product name or
        active ingredient, e.g. 'PARACETAMOL' is found in
        'SUNNY PARACETAMOL TABLET 500 MG'. Returns False for an empty
        medicine. Expects the medicine to already be stripped and uppercased
        by format_ai_output.

        Uses the same lookup as logic_manager's routing, so a medicine that
        passes validation always has an HSA classification to route with.
        """

        # An empty medicine is never valid. This check is needed because ''
        # is found inside every dataset entry, so it would wrongly return True.
        if ai_medicine == "":
            return False

        return self.__classify_medicine(ai_medicine, self.__hsa_df) is not None     