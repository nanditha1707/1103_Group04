import pandas as pd

from data_manager.storage import RecordReader


class PatientQuery:
    """Finds a patient in the saved records, chooses how to show the
    result and saves it to CSV."""

    def __init__(
        self, reader: RecordReader, identifier_columns: list[str]
    ):
        self.__reader = reader
        self.__identifier_columns = identifier_columns

    def find_by_queue(
        self,
        queue_number: str,
        filter_columns: list[str],
        date: str
    ) -> pd.DataFrame | None:
        """Find the patient with the given queue number on the given
        date. Return a DataFrame of their record with only the
        filter_columns, which is empty if no patient matches, or None if
        there are no records."""
        return self.__reader.find_by_queue(queue_number, filter_columns, date)

    def find_by_date(self, filter_columns: list[str], date: str) -> pd.DataFrame | None:
        # Each patient gets their own row, so the time and queue number
        # are added in front to tell the rows apart, unless the filter
        # already has them.
        identifier_columns = []
        for column in self.__identifier_columns:
            if column not in filter_columns:
                identifier_columns.append(column)

        return self.__reader.find_by_date(identifier_columns + filter_columns, date)
