from collections.abc import Callable

import pandas as pd

from .constants import DIAGNOSIS_FIELDS, EXPLANATION_FIELDS, MEDICINE_FIELDS


class OutputValidator:
    _EMERGENCY_WORD = "EMERGENCY"

    def __init__(
        self, icd_df: pd.DataFrame | None, hsa_df: pd.DataFrame | None, classify_medicine: Callable[[str, pd.DataFrame], str | None]
    ):
        self.__icd_df = icd_df
        self.__hsa_df = hsa_df
        self.__classify_medicine = classify_medicine

    @property
    def has_icd_data(self) -> bool:
        return self.__icd_df is not None

    def is_valid(self, output: dict) -> bool:
        diagnosis_checks = [
            self.diagnosis_is_valid(output[title_field], output[code_field])
            for title_field, code_field in DIAGNOSIS_FIELDS
        ]
        if not all(diagnosis_checks):
            return False

        if self.__hsa_df is None:
            return True

        medicine_checks = [
            self.medicine_is_valid(output[field]) for field in MEDICINE_FIELDS
        ]
        if all(medicine_checks):
            return True

        explanations = [output[field] for field in EXPLANATION_FIELDS]
        return any(self._EMERGENCY_WORD in text for text in explanations)

    def diagnosis_is_valid(self, title: str, code: str) -> bool:
        is_match = (
            (self.__icd_df["DiseaseName"] == title)
            & (self.__icd_df["Code"] == code)
        )

        return bool(is_match.any())

    def medicine_is_valid(self, medicine: str) -> bool:
        if medicine == "":
            return False

        return self.__classify_medicine(medicine, self.__hsa_df) is not None
