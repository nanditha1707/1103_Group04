import pandas as pd

from dataset import Dataset


class HsaDataset(Dataset):
    """The HSA dataset: registered drugs and their classification."""

    def clean(self, hsa_df: pd.DataFrame) -> pd.DataFrame:
        """Return the HSA dataset with only the required drug columns,
        cleaned and without duplicates."""

        return self._standardise(
            hsa_df,
            column_map={
                "Productname": "DrugName",
                "Dosageform": "Dosage",
                "Strength": "Strength",
                "Activeingredients": "ActiveIngredients",
                "ATCCode": "ATCCode",
                "Forensicclassification": "Classification"
            },
            uppercase_columns=("DrugName", "ActiveIngredients")
        )