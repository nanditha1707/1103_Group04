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
    def load_cleaned(self) -> pd.DataFrame | None:
        """Load and clean the dataset. Return None if it fails to load."""
        try:
            dataset_df = pd.read_csv(
                self.__csv_path,
                low_memory=False
            )

        except (FileNotFoundError, pd.errors.ParserError):
            return None

        return self.clean(dataset_df)

# ======================================================================
# DATASET CLEANING FUNCTIONS
# ======================================================================
    @property
    @abstractmethod
    def _columns_to_keep(self) -> dict[str, str]:
        pass

    @property
    @abstractmethod
    def _columns_to_uppercase(self) -> tuple[str, ...]:
        pass

    def clean(self, dataset_df: pd.DataFrame) -> pd.DataFrame:
        dataset_df = self._keep_columns(dataset_df, self._columns_to_keep)
        dataset_df = self.replace_blank_values(dataset_df)
        dataset_df = self._drop_incomplete_rows(dataset_df)
        dataset_df = self._strip_spaces(dataset_df)
        dataset_df = self._uppercase(dataset_df, self._columns_to_uppercase)
        dataset_df = self._drop_duplicates(dataset_df)
        return dataset_df

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

    @staticmethod
    def _keep_columns(dataset_df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
        # Keep only the required columns, then rename them.
        dataset_df = dataset_df[list(column_map)].copy()
        dataset_df = dataset_df.rename(columns=column_map)
        return dataset_df

    @staticmethod
    def _drop_incomplete_rows(dataset_df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows that are missing important information.
        dataset_df = dataset_df.dropna()
        return dataset_df

    @staticmethod
    def _strip_spaces(dataset_df: pd.DataFrame) -> pd.DataFrame:
        for column in dataset_df.columns:
            dataset_df[column] = dataset_df[column].astype(str).str.strip()
        return dataset_df

    @staticmethod
    def _uppercase(dataset_df: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
        for column in columns:
            dataset_df[column] = dataset_df[column].str.upper()

        return dataset_df

    @staticmethod
    def _drop_duplicates(dataset_df: pd.DataFrame) -> pd.DataFrame:
        # Remove duplicate rows, then reset the index.
        dataset_df = dataset_df.drop_duplicates()
        dataset_df = dataset_df.reset_index(drop=True)
        return dataset_df
