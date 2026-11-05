from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import pandas as pd


class Dataset(ABC):
    """A dataset (ICD-11 or HSA) can be loaded from a CSV
    and cleaned. Each subclass says which columns to keep and how to
    clean them."""

    def __init__(self, csv_path: Path):
        self._csv_path = csv_path

# ======================================================================
# DATASET LOADING FUNCTIONS
# ======================================================================
    @staticmethod
    def read_csv(csv_path: Path) -> pd.DataFrame | None:
        """Load a dataset CSV. Return None if the file is missing or
        cannot be read."""
 
        try:
            return pd.read_csv(
                csv_path,
                low_memory=False
            )
 
        except (FileNotFoundError, pd.errors.ParserError):
            return None
 
    def load(self) -> pd.DataFrame | None:
        """Load this dataset's CSV. Return None if it cannot be read."""
        return self.read_csv(self._csv_path)

# ======================================================================
# DATASET CLEANING FUNCTIONS
# ======================================================================
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

