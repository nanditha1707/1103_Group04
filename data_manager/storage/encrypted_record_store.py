import pandas as pd

from data_manager.security import Cipher, RecordEncryptor

from .record_store import RecordStore

class EncryptedRecordStore(RecordStore):
    """
    Encrypts sensitive columns before the record is saved and decrypted after a query.
    Implemented this way to keep the encryption and decryption logic isolated. 
    The subclass works akin to a decorator, extending the functionality of RecordStore.
    """

    def __init__(
        self, record_store: RecordStore, cipher: Cipher, encrypted_columns: list[str]
    ):
        self.__record_store = record_store
        self.__encryptor = RecordEncryptor(cipher, encrypted_columns)

    def save(self, record: dict) -> str | None:
        encrypted_record = self.__encryptor.encrypt_record(record)
        return self.__record_store.save(encrypted_record)

    def find_by_queue(self, queue_number: str, columns: list[str], date: str) -> pd.DataFrame | None:
        table = self.__record_store.find_by_queue(queue_number, columns, date)
        return self.__decrypt(table)

    def find_by_date(self, columns: list[str], date: str) -> pd.DataFrame | None:
        table = self.__record_store.find_by_date(columns, date)
        return self.__decrypt(table)

    def __decrypt(self, table: pd.DataFrame | None) -> pd.DataFrame | None:
        # None means the database could not be reached, 
        # so it returns None to main.py to show the database error message.
        if table is None:
            return None

        try:
            return self.__encryptor.decrypt_table(table)
        # Only occurs when decryption fails. The existing checks ensure it is not a wrong key, 
        # thus in the unlikely scenario this edge case occurs, 
        # it will be treated as a database error. It is essentially a edgecase guard.
        except ValueError:
            return None
