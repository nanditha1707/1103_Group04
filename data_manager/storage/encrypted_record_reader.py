import pandas as pd

from data_manager.security import RecordEncryptor

from .record_reader import RecordReader


class EncryptedRecordReader(RecordReader):
    """
    Finds records through another RecordReader and then decrypts their sensitive columns.
    It wraps that reader like a decorator so the decryption logic stays out of the database code.
    """

    def __init__(
        self, reader: RecordReader, encryptor: RecordEncryptor
    ):
        self.__reader = reader
        self.__encryptor = encryptor

    def find_by_queue(self, queue_number: str, columns: list[str], date: str) -> pd.DataFrame | None:
        table = self.__reader.find_by_queue(queue_number, columns, date)
        return self.__decrypt(table)

    def find_by_date(self, columns: list[str], date: str) -> pd.DataFrame | None:
        table = self.__reader.find_by_date(columns, date)
        return self.__decrypt(table)

    def __decrypt(self, table: pd.DataFrame | None) -> pd.DataFrame | None:
        # None means the database could not be reached
        # so it returns None for the portal to show the database error message.
        if table is None:
            return None

        try:
            return self.__encryptor.decrypt_table(table)
        # Only occurs when decryption fails. The existing checks ensure it is not a wrong key,
        # thus in the unlikely scenario this edge case occurs,
        # it will be treated as a database error. It is essentially a edgecase guard.
        except ValueError:
            return None
