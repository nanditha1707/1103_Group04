from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import pandas as pd


class Dataset(ABC):
    """A dataset (ICD-11 or HSA) can be loaded from a CSV
    and cleaned. Each subclass says which columns to keep and how to
    clean them."""

    def __init__(
        self, csv_path: Path
    ):
        self.__csv_path = csv_path

# ======================================================================
# DATASET LOADING FUNCTIONS
# ======================================================================
    def load(self) -> pd.DataFrame | None:
        """Load this dataset's CSV. Return None if it cannot be read."""
        try:
            return pd.read_csv(
                self.__csv_path,
                low_memory=False
            )

        except (FileNotFoundError, pd.errors.ParserError):
            return None

    def get_cleaned(self) -> pd.DataFrame | None:
        """Load and clean the dataset. Return None if it fails to load."""
        dataset_df = self.load()

        if dataset_df is None:
            return None

        return self.clean(dataset_df)

# ======================================================================
# DATASET CLEANING FUNCTIONS
# ======================================================================
    @abstractmethod
    def clean(self, dataset_df: pd.DataFrame) -> pd.DataFrame:
        """Return the cleaned dataset. Every dataset type cleans its own
        columns, so each subclass must provide this."""

    @staticmethod
    def replace_blank_values(dataset_df: pd.DataFrame) -> pd.DataFrame:
        """Return the dataset with empty and dash values replaced by NaN,
        so they can be removed with dropna."""

        # Replace empty strings with NaN.
        dataset_df = dataset_df.replace(
            r"^\s*$",
            np.nan,
            regex=True
        )

        # Replace dash values with NaN.
        dataset_df = dataset_df.replace(
            r"^\s*[-–—]+\s*$",
            np.nan,
            regex=True
        )

        return dataset_df

    def _standardise(
        self,
        dataset_df: pd.DataFrame,
        column_map: dict[str, str],
        uppercase_columns: tuple[str, ...]
    ) -> pd.DataFrame:
        """Shared cleaning steps for both datasets. Keep only the columns in column_map
        (renamed to its values), remove rows with missing values, strip
        extra spaces, uppercase the given columns and remove duplicates."""

        # Keep only the required columns, then rename them.
        dataset_df = dataset_df[list(column_map)].copy()
        dataset_df = dataset_df.rename(columns=column_map)

        dataset_df = self.replace_blank_values(dataset_df)

        # Remove rows that are missing important information.
        dataset_df = dataset_df.dropna(subset=list(column_map.values()))

        # Remove extra spaces, and uppercase where needed.
        for column in dataset_df.columns:
            cleaned_column = dataset_df[column].astype(str).str.strip()

            if column in uppercase_columns:
                cleaned_column = cleaned_column.str.upper()

            dataset_df[column] = cleaned_column

        # Remove duplicate rows, then reset the index.
        dataset_df = dataset_df.drop_duplicates()
        dataset_df = dataset_df.reset_index(drop=True)

        return dataset_df
