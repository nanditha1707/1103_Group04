import os

from dotenv import load_dotenv

from data_manager import constants
from data_manager.manager import DataManager
from data_manager.patients import PatientQuery, QueryExporter, RecordSaver
from data_manager.dataset import HsaDataset, IcdDataset, SymptomDataset
from data_manager.reports import ReportGenerator
from data_manager.storage import Database, PostgresDatabase, PostgresRecordStore


class DataManagerFactory:
    @staticmethod
    def create(database: Database | None = None) -> DataManager:
        if database is None:
            load_dotenv(override=True)
            database_url = os.getenv(constants.DATABASE_URL_ENV_VAR)
            database = PostgresDatabase(database_url)

        record_store = PostgresRecordStore(database)

        return DataManager(
            IcdDataset(constants.ICD_CSV_PATH),
            HsaDataset(constants.HSA_CSV_PATH),
            SymptomDataset(constants.SYMPTOMS_CSV_PATH),
            RecordSaver(record_store, constants.RECORD_COLUMNS),
            PatientQuery(record_store, constants.IDENTIFIER_COLUMNS),
            QueryExporter(constants.QUERY_DIR, constants.SGT),
            ReportGenerator(record_store, constants.ROUTE_LABELS),
            record_store)
