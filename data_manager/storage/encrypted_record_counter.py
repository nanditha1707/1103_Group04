from collections import Counter

from .record_counter import RecordCounter
from .record_reader import RecordReader
from .route_counter import RouteCounter


class EncryptedRecordCounter(RecordCounter):
    """
    Counts the daily report figures while the medicine columns are encrypted. 
    Fernet encrypts the same medicine differently every time,
    so medicines cannot be counted in SQL. 
    As such, they are read through a reader that decrypts and counts them in Python instead. 
    Routes are not encrypted, so route counts come straight from the database.
    """

    def __init__(
        self, decrypting_reader: RecordReader, route_counter: RouteCounter, medicine_columns: list[str]
    ):
        self.__decrypting_reader = decrypting_reader
        self.__route_counter = route_counter
        self.__medicine_columns = medicine_columns

    def count_medicine(self, medicine: str, date: str) -> int | None:
        medicines_issued = self.__get_medicines_issued(date)
        if medicines_issued is None:
            return None

        return medicines_issued.count(medicine)

    def count_each_medicine(self, date: str) -> dict[str, int] | None:
        medicines_issued = self.__get_medicines_issued(date)
        if medicines_issued is None:
            return None

        # Sort by highest to lowest count, and then name from A-Z as a tiebreaker,
        # We dont use reverse=True as that would cause the name order to swap to Z-A.
        medicine_counts = sorted(
            Counter(medicines_issued).items(),
            # Negates the value becaused of how sorted works, 
            # swapping the order from ascending to descending.
            key=lambda item: (-item[1], item[0])
        )
        return dict(medicine_counts)

    def count_each_route(self, date: str) -> dict[str, int] | None:
        return self.__route_counter.count_each_route(date)

    def __get_medicines_issued(self, date: str) -> list[str] | None:
        """
        Return every medicine issued on the date, 
        one entry per time it was issued, or None if the records could not be read.
        """
        # Queries the SQL database and decrpts the relevant columns.
        table = self.__decrypting_reader.find_by_date(self.__medicine_columns, date)
        if table is None:
            return None

        medicines_issued = []
        for column in self.__medicine_columns:
            for medicine in table[column]:
                # Skip empty values
                if isinstance(medicine, str) and medicine != "":
                    medicines_issued.append(medicine)

        return medicines_issued
