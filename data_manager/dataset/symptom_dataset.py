import pandas as pd

from .dataset import Dataset


class SymptomDataset(Dataset):
    def clean(self, dataset_df: pd.DataFrame) -> pd.DataFrame:
        symptoms_df = dataset_df[["term"]].copy()
        symptoms_df["term"] = symptoms_df["term"].str.upper()

        return symptoms_df
