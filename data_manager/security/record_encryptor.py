import pandas as pd

from .cipher import Cipher


class RecordEncryptor:
    """
    Applies a Cipher to the sensitive columns of a patient record efore it is saved, 
    and of a query result after it is read.
    """

    def __init__(
        self, cipher: Cipher, encrypted_columns: list[str]
    ):
        self.__cipher = cipher
        self.__encrypted_columns = encrypted_columns

    def encrypt_record(self, record: dict) -> dict:
        """
        Return a copy of the record with every sensitive column
        encrypted. Missing values (None) stay None so the database still
        saves them as NULL.
        """
        # Creates a shallow copy of the dict, which is adequate for the use case.
        encrypted_record = dict(record)
        for column in self.__encrypted_columns:
            value = encrypted_record.get(column)
            if value is not None:
                # Encrypts the column value in the copy of the dict.
                encrypted_record[column] = self.__cipher.encrypt(str(value))
        # Returns the shallow copy.
        return encrypted_record

    def decrypt_table(self, table: pd.DataFrame) -> pd.DataFrame:
        """
        Return a copy of the query result with every sensitive column that is in it decrypted. 
        Columns left out by the filter option are skipped. 
        Raise ValueError if a value cannot be decrypted.
        """
        decrypted_table = table.copy()
        for column in self.__encrypted_columns:
            # Checks if any of the columns in the query need to be decrypted.
            if column in decrypted_table.columns:
                # Calls decrypt_value once for each of the values in the column
                decrypted_table[column] = decrypted_table[column].map(self.__decrypt_value)
                # Calls decrypt_value once for each of the values in the column. 
                # Empty values are skipped and left as they are.
                decrypted_table[column] = decrypted_table[column].map(
                    self.__cipher.decrypt, na_action="ignore")

        return decrypted_table
