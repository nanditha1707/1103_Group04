import os

from dotenv import load_dotenv

from data_manager import constants
from data_manager.dataset import HsaDataset, IcdDataset, SymptomDataset
from data_manager.manager import DataManager
from data_manager.patients import PatientQuery, QueryExporter, RecordSaver
from data_manager.reports import ReportGenerator
from data_manager.security import Cipher, EncryptionKeyError, FernetCipher, KeyVerifier
from data_manager.storage import (
    Database,
    EncryptedRecordCounter,
    EncryptedRecordStore,
    PostgresDatabase,
    PostgresKeyCheckStore,
    PostgresRecordStore,
)


class DataManagerFactory:
    @staticmethod
    def load_symptoms() -> list[str]:
        """Return every symptom name from the local symptoms CSV. 
        Needs no database or encryption key, 
        so the IO manager can be created before create() checks the key."""
        return SymptomDataset(constants.SYMPTOMS_CSV_PATH).load_terms()

    @staticmethod
    def create(database: Database | None = None, cipher: Cipher | None = None) -> DataManager:
        # Both the database URL and the encryption key are in the .env file.
        load_dotenv(override=True)
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

        # Check the key against the database before anything can be saved.
        key_verifier = KeyVerifier(
            cipher,
            PostgresKeyCheckStore(database),
            constants.KEY_CHECK_TEXT
        )
        key_error = key_verifier.verify()
        if key_error is not None:
            raise EncryptionKeyError(key_error)

        table_name = os.getenv(constants.RECORDS_TABLE_ENV_VAR) or constants.DEFAULT_RECORDS_TABLE
        record_store = PostgresRecordStore(database, table_name)

        # Saving and patient queries go through the encrypted store.
        # Queue numbers only use columns that are not encrypted, so they keep using the plain record store.
        encrypted_store = EncryptedRecordStore(
            record_store,
            cipher,
            constants.ENCRYPTED_COLUMNS
        )

        # The medicine reports count the decrypted medicines in Python.
        # Route counts still come from the plain record store.
        encrypted_counter = EncryptedRecordCounter(
            encrypted_store,
            record_store,
            constants.MEDICINE_COLUMNS
        )

        return DataManager(
            IcdDataset(constants.ICD_CSV_PATH),
            HsaDataset(constants.HSA_CSV_PATH),
            RecordSaver(encrypted_store, constants.RECORD_COLUMNS),
            PatientQuery(encrypted_store, constants.IDENTIFIER_COLUMNS),
            QueryExporter(constants.QUERY_DIR, constants.SGT),
            ReportGenerator(encrypted_counter, constants.ROUTE_LABELS),
            record_store)
