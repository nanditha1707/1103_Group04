from pathlib import Path
 
import pandas as pd
 
class PatientRecord:
    """Reads and writes the patient records CSV."""
 
    def __init__(
        self,
        records_path: Path,
        seed_path: Path,
        columns: list[str]
    ):
        self.__records_path = records_path
        self.__seed_path = seed_path
        self.__columns = columns