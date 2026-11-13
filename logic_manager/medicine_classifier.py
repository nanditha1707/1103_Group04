import pandas as pd

from .classification import Classification


class MedicineClassifier:
    """
    Looks up the HSA classification of a medicine.
    """

    def __init__(self, hsa_df: pd.DataFrame):
        # Private: only this class reads the HSA dataset.
        self.__hsa_df = hsa_df

    def classify(self, medicine: str) -> Classification | None:
        """
        Return the HSA classification of a medicine. 
        If the medicine matches several rows, the least restrictive classification is returned, 
        because if the same medicine is available at a retail store, 
        they can be routed to a pharmacist for assessmentcrather then seeing the doctor.
        Returns None if the medicine is not in the HSA dataset.
        """

        # Compare in lower case so "paracetamol" matches "Paracetamol".
        target = self._to_text(medicine)

        # An empty medicine name would match every row, so skip it.
        if not target:
            return None

        # Every valid classification found for this medicine.
        found = []

        # zip() walks the three columns together, one row at a time.
        # Unlike hsa_df["DrugName"][row], this does not depend on the dataframe index, 
        # so it still works after rows are filtered or dropped.
        for drug_name, ingredient, classification_text in zip(
            self.__hsa_df["DrugName"],
            self.__hsa_df["ActiveIngredients"],
            self.__hsa_df["Classification"]
        ):
            if not self._matches(target, drug_name, ingredient):
                continue

            classification = Classification.from_text(classification_text)
            if classification is not None:
                found.append(classification)

        # Medicine is not in the HSA dataset.
        if not found:
            return None

        return Classification.least_restrictive(found)

    def _matches(self, target: str, drug_name, ingredient) -> bool:
        """
        Return True if the medicine appears in the drug name or the active ingredients of a row.
        """
        drug_name_text = self._to_text(drug_name)
        ingredient_text = self._to_text(ingredient)

        in_drug_name = target in drug_name_text
        in_ingredient = target in ingredient_text

        return in_drug_name or in_ingredient

    @staticmethod
    def _to_text(value) -> str:
        if pd.isna(value):
            return ""
        return str(value)
