from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pandas as pd


class QueryExporter:
    def __init__(
        self, query_dir: Path, clock: Callable[[], datetime]
    ):
        self.__query_dir = query_dir
        self.__clock = clock

    def export(self, query_df: pd.DataFrame) -> bool:
        """Save the query results to a new timestamped CSV in the query
        folder. Return True if saved, False if the file could not be
        written."""
        timestamp = self.__clock().strftime("%Y%m%d_%H%M%S")
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

    def clear(self) -> None:
        """Delete every exported query CSV and the query folder if it is
        then empty. Called when the program exits so decrypted patient
        data does not stay on disk, and again at startup to remove files
        left behind if the program was closed without exiting normally.
        A file that cannot be deleted (e.g. still open in Excel) is left
        and removed on the next run."""
        # is_dir() checks the query folder exists. If nothing was exported yet there is nothing to delete.
        if not self.__query_dir.is_dir():
            return
        # glob() finds every file in the folder whose name matches query_*.csv
        # so only the exported query files are deleted.
        for query_csv_path in self.__query_dir.glob("query_*.csv"):
            try:
                # unlink() deletes the file.
                query_csv_path.unlink()
            # The file is open in another program (e.g. Excel) and cannot be deleted yet.
            except OSError:
                pass
        try:
            # rmdir() deletes the query folder. It only works if the folder is empty.
            self.__query_dir.rmdir()
        # The folder still has a file in it or is mounted by Docker.
        except OSError:
            pass
