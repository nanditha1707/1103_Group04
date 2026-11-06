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

    def find_by_queue(
        self,
        queue_number: str,
        filter_columns: list[str],
        today: str
    ) -> pd.DataFrame | None:
        """Find the patient with the given queue number on the given
        date. Return a DataFrame of their record with only the
        filter_columns, which is empty if no patient matches, or None if
        there are no records."""
 
        # Checks if records exist. If they do,
        # continues with the block.
        if self.__records is not None and not self.__records.empty:
            # @ lets query use the local variables queue_number and today.
            patient = self.__records.query(
                "queue_number == @queue_number and date == @today"
            )
            return patient[filter_columns]
 
        # If there are no records, return None.
        return None

    @staticmethod
    def choose_output(filter_columns: list[str]) -> str:
        """Return "print" if a table with these columns fits in the
        terminal, otherwise "export" so it is saved to a CSV instead."""
        # Each column is at least 10 characters wide (the table's
        # maxcolwidths), but a long column name needs more than that.
        width_needed = len(filter_columns) * 10
        header_width_needed = sum(len(item) for item in filter_columns)
        width_needed = max(width_needed, header_width_needed)
 
        terminal_width = shutil.get_terminal_size().columns
 
        if terminal_width >= width_needed:
            return "print"
 
        return "export"

    def export(self, query_df: pd.DataFrame) -> bool:
        """Save the query results to a new timestamped CSV in the query
        folder. Return True if saved, False if the file could not be
        written."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_csv_path = self.__query_dir / f"query_{timestamp}.csv"
 
        try:
            # Creates the query folder if it does not exist yet.
            self.__query_dir.mkdir(exist_ok=True)
 
            # Writes the df to a new CSV file with a header.
            # The timestamp in the file name keeps each export separate.
            query_df.to_csv(
                query_csv_path,
                mode="w",
                index=False,
                encoding="utf-8"
            )
 
        # The file is open in another program (e.g. Excel) or cannot be
        # written.
        except OSError:
            return False
 
        return True
 