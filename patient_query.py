from datetime import datetime
from pathlib import Path
import shutil
 
import pandas as pd
 
 
class PatientQuery:
    """Finds a patient in the saved records, chooses how to show the
    result and saves it to CSV."""
 
    def __init__(
        self,
        records: pd.DataFrame | None,
        query_dir: Path,
        filter_columns: dict[int, list[str]]
    ):
        self.__records = records
        self.__query_dir = query_dir
        # Maps each filter menu option (1 to 4) to its record columns.
        self.__filter_columns = filter_columns

    def get_filter(self, option: str) -> list[str] | None:
        """Return the record columns for a filter menu option (1 to 4).
        Return None for any other option number. Expects option to
        already be checked as a positive whole number by
        io_manager.validate_option."""
        return self.__filter_columns.get(int(option))