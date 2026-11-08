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

    def has_icd_data(self) -> bool:
        """Return True if the ICD-11 dataset loaded. Without it the
        diagnoses cannot be checked."""
        return self.__icd_df is not None

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
    
    def validate(self, ai_output: dict) -> bool:
        """
        Check the AI output against the ICD11 and HSA datasets.

        Validation passes in only 2 cases:
        1. Normal case: both diagnoses match the ICD-11 dataset AND all 4
           medicines match the HSA dataset.
        2. Emergency case: both diagnoses match the ICD11 dataset AND at
           least one explanation contains the word "EMERGENCY". The
           medicines are not checked because the AI is instructed to 
           leave them empty since its better for a doctor to decide in a
           real emergency as emergencies are complex.
        Everything else fails validation.
        """

        # Step 1: Check that both diagnoses and codes match the ICD11 dataset.
        # They return True if valid and False otherwise.
        primary_diagnosis_is_valid = self.validate_diagnosis(
            ai_output["primary_diagnosis_ICD11_Title"],
            ai_output["primary_diagnosis_ICD11_Code"],
        )
        secondary_diagnosis_is_valid = self.validate_diagnosis(
            ai_output["secondary_diagnosis_ICD11_Title"],
            ai_output["secondary_diagnosis_ICD11_Code"],
        )

        # Return False if either doesn't match. Only pass validation when
        # both primary and secondary diagnosis are valid.
        if not primary_diagnosis_is_valid or not secondary_diagnosis_is_valid:
            return False

        # Without HSA data the medicines cannot be checked. logic_manager
        # sends the patient to a doctor in that case, so only the diagnoses
        # need to be valid.
        if self.__hsa_df is None:
            return True

        # Step 2: Collect the 4 medicine fields into a list so they can be
        # checked one at a time.
        medicines = [
            ai_output["primary_diagnosis_medicine_1"],
            ai_output["primary_diagnosis_medicine_2"],
            ai_output["secondary_diagnosis_medicine_1"],
            ai_output["secondary_diagnosis_medicine_2"],
        ]

        # Step 3: Count how many medicines match the HSA dataset.
        valid_medicine_count = 0

        for medicine in medicines:
            if self.validate_medicine(medicine):
                valid_medicine_count += 1

        # Case 1 (normal): all 4 medicines are valid and the 2 diagnosis match.
        if valid_medicine_count == 4:
            return True

        # Step 4: Check if either explanation contains the word "EMERGENCY".
        primary_explanation = ai_output["primary_diagnosis_explanation"]
        secondary_explanation = ai_output["secondary_diagnosis_explanation"]

        # Case 2 (emergency): the medicines didn't all match, but it is an
        # emergency so they are not needed.
        if "EMERGENCY" in primary_explanation or "EMERGENCY" in secondary_explanation:
            return True

        # Any other combination fails validation.
        return False