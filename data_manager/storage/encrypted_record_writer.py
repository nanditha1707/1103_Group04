from data_manager.security import RecordEncryptor

from .record_writer import RecordWriter


class EncryptedRecordWriter(RecordWriter):
    """
    Encrypts the sensitive columns of a record and then saves it through another RecordWriter.
    It wraps that writer like a decorator so the encryption logic stays out of the database code.
    """

    def __init__(
        self, writer: RecordWriter, encryptor: RecordEncryptor
    ):
        self.__writer = writer
        self.__encryptor = encryptor

    def save(self, record: dict) -> str | None:
        encrypted_record = self.__encryptor.encrypt_record(record)
        return self.__writer.save(encrypted_record)
