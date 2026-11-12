import pandas as pd
from .constants import DIAGNOSIS_FIELDS, EXPLANATION_FIELDS, MEDICINE_FIELDS


class OutputValidator:
    """Checks a parsed AI output against the cleaned ICD-11 and HSA
    datasets.

    Validation passes in only 2 cases:
    1. Normal case: both diagnoses match the ICD-11 dataset AND all 4
       medicines match the HSA dataset.
    2. Emergency case: both diagnoses match the ICD-11 dataset AND at
       least one explanation contains the word "EMERGENCY". The medicines
       are not checked because the AI is instructed to leave them empty,
       since it is better for a doctor to decide in a real emergency.
    Everything else fails validation.
    """

    # Word the AI puts in an explanation when the patient needs urgent care.
    _EMERGENCY_WORD = "EMERGENCY"

    def __init__(
        self, icd_df: pd.DataFrame | None, hsa_df: pd.DataFrame | None
    ):
        # The cleaned datasets loaded by data_manager. Either can be None if
        # it failed to load.
        self.__icd_df = icd_df
        self.__hsa_df = hsa_df

    @property
    def has_icd_data(self) -> bool:
        """True if the ICD-11 dataset loaded. Without it no diagnosis can
        be checked."""
        return self.__icd_df is not None

    def diagnosis_is_valid(self, title: str, code: str) -> bool:
            """Return True only if the title and code are an exact match on
            the same row, so a real title paired with the wrong code fails.
    
            Expects the title and code to already be stripped and uppercased by
            ReplyParser, the same as the cleaned dataset.
            """
            is_match = (
                (self.__icd_df["DiseaseName"] == title)
                & (self.__icd_df["Code"] == code)
            )
    
            return bool(is_match.any())
    
    def medicine_is_valid(self, medicine: str) -> bool:
        """Return True if the medicine is found inside any HSA product name
        or active ingredient, e.g. 'PARACETAMOL' is found in
        'SUNNY PARACETAMOL TABLET 500 MG'.

        Expects the medicine to already be stripped and uppercased by
        ReplyParser, the same as the cleaned dataset. The cleaned dataset
        drops rows without a classification, so a medicine that passes
        always has one for logic_manager to route with.
        """
        # An empty medicine is never valid. This check is needed because ''
        # is found inside every dataset entry, so it would wrongly pass.
        if medicine == "":
            return False
        
        is_match = (
            self.__hsa_df["DrugName"].str.contains(medicine, regex=False)
            | self.__hsa_df["ActiveIngredients"].str.contains(medicine, regex=False)
        )

        return bool(is_match.any())

    def is_valid(self, output: dict) -> bool:
        """Return True if the output passes one of the 2 cases above."""
        # Step 1: Both diagnoses must match the ICD-11 dataset.
        diagnosis_checks = [
            self.diagnosis_is_valid(output[title_field], output[code_field])
            for title_field, code_field in DIAGNOSIS_FIELDS
        ]
        if not all(diagnosis_checks):
            return False

        # Without HSA data the medicines cannot be checked. logic_manager
        # sends the patient to a doctor in that case, so only the diagnoses
        # need to be valid.
        if self.__hsa_df is None:
            return True

        # Step 2a (normal case): all 4 medicines match the HSA dataset.
        medicine_checks = [
            self.medicine_is_valid(output[field])
            for field in MEDICINE_FIELDS
        ]
        if all(medicine_checks):
            return True

        # Step 2b (emergency case): the medicines did not all match but they
        # are not needed if either explanation field says it is an emergency.
        explanations = [
            output[field]
            for field in EXPLANATION_FIELDS
        ]

        # For text in explanation fields, if emergency word in text then return
        # True else return False.
        return any(
            self._EMERGENCY_WORD in text
            for text in explanations
        )
