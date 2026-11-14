from .record_reader import RecordReader
from .record_writer import RecordWriter


class RecordStore(RecordWriter, RecordReader):
    """
    A interface that combines RecordWriter and RecordReader, meant for classes that need both, 
    such as the EncryptedRecordStore and PostgresRecordStore
    """