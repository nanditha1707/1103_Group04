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

    