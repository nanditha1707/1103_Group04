from datetime import datetime, tzinfo
from pathlib import Path

import pandas as pd


class QueryExporter:
    def __init__(
        self, query_dir: Path, timezone: tzinfo
    ):
        self.__query_dir = query_dir
        self.__timezone = timezone

    def export(self, query_df: pd.DataFrame) -> bool:
        """Save the query results to a new timestamped CSV in the query
        folder. Return True if saved, False if the file could not be
        written."""
        timestamp = datetime.now(self.__timezone).strftime("%Y%m%d_%H%M%S")
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
