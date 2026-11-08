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