import pandas as pd

from dataset import Dataset


class IcdDataset(Dataset):
    """The ICD-11 dataset: disease codes and names."""

    def clean(self, icd_df: pd.DataFrame) -> pd.DataFrame:
        """Return the ICD-11 dataset with only the disease codes and
        names, cleaned and without duplicates. Code and name are
        uppercased to match the formatted AI output."""

        return self._standardise(
            icd_df,
            column_map={
                "Code": "Code",
                "Title": "DiseaseName"
            },
            uppercase_columns=("Code", "DiseaseName")
        )