import os
from collections.abc import Callable
from datetime import datetime

from data_manager import constants
from data_manager.dataset import HsaDataset, IcdDataset, SymptomDataset
from data_manager.manager import DataManager
from data_manager.patients import PatientQuery, QueryExporter, RecordSaver
from data_manager.reports import ReportGenerator
from data_manager.security import Cipher, EncryptionKeyError, FernetCipher, KeyCheckStore, KeyVerifier, RecordEncryptor
from data_manager.storage import (
    Database,
    EncryptedRecordCounter,
    EncryptedRecordReader,
    EncryptedRecordWriter,
    PostgresDatabase,
    PostgresKeyCheckStore,
    PostgresQueueNumberSource,
    PostgresRecordReader,
    PostgresRecordWriter,
    PostgresRouteCounter,
)


class DataManagerFactory:
    @staticmethod
    def load_symptoms() -> list[str]:
        """Return every symptom name from the local symptoms CSV. 
        Needs no database or encryption key, 
        so the IO manager can be created before create() checks the key."""
        return SymptomDataset(constants.SYMPTOMS_CSV_PATH).load_terms()

    @staticmethod
    def create(
        clock: Callable[[], datetime], database: Database | None = None, cipher: Cipher | None = None, key_check_store: KeyCheckStore | None = None
    ) -> DataManager:
        if database is None:
            database_url = os.getenv(constants.DATABASE_URL_ENV_VAR)
            database = PostgresDatabase(database_url)

        if cipher is None:
            encryption_key = os.getenv(constants.ENCRYPTION_KEY_ENV_VAR)
            try:
                cipher = FernetCipher(encryption_key)
            # FernetCipher raises ValueError for a missing or malformed key.
            except ValueError as error:
                raise EncryptionKeyError(str(error)) from error

        if key_check_store is None:
            key_check_store = PostgresKeyCheckStore(database)

        # Check the key against the database before anything can be saved.
        key_verifier = KeyVerifier(
            cipher,
            key_check_store,
            constants.KEY_CHECK_TEXT
        )
        key_error = key_verifier.verify()
        if key_error is not None:
            raise EncryptionKeyError(key_error)

        table_name = os.getenv(constants.RECORDS_TABLE_ENV_VAR) or constants.DEFAULT_RECORDS_TABLE
        encryptor = RecordEncryptor(cipher, constants.ENCRYPTED_COLUMNS)

        # Saving and patient queries go through the encrypted record writer and reader.
        record_writer = EncryptedRecordWriter(
            PostgresRecordWriter(database, table_name),
            encryptor
        )
        record_reader = EncryptedRecordReader(
            PostgresRecordReader(database, table_name),
            encryptor
        )

        # The medicine reports count the decrypted medicines in Python.
        # Routes are not encrypted so the database counts them directly.
        encrypted_counter = EncryptedRecordCounter(
            record_reader,
            PostgresRouteCounter(database, table_name),
            constants.MEDICINE_COLUMNS
        )

        # Queue numbers only use columns that are not encrypted so they are read straight from the database.
        return DataManager(
            IcdDataset(constants.ICD_CSV_PATH),
            HsaDataset(constants.HSA_CSV_PATH),
            RecordSaver(record_writer, constants.RECORD_COLUMNS),
            PatientQuery(record_reader, constants.IDENTIFIER_COLUMNS),
            QueryExporter(constants.QUERY_DIR, clock),
            ReportGenerator(encrypted_counter, constants.ROUTE_LABELS),
            PostgresQueueNumberSource(database, table_name),
            clock)
