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

    