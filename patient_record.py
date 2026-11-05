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

    def create_file_if_missing(self) -> None:
        """Copy the starter records into the records folder if there is no
        patient records CSV yet. Existing records are never overwritten."""
        if self.__records_path.exists():
            return
 
        try:
            self.__records_path.parent.mkdir(exist_ok=True)
            # Read the seed file first, so if it is missing the records
            # file is never created.
            # "b" copies the bytes exactly in binary mode, so copy is
            # identical to the seed.
            with open(self.__seed_path, "rb") as seed_file:
                seed_contents = seed_file.read()
 
            # Create the records file and write the seed contents into it.
            with open(self.__records_path, "wb") as records_file:
                records_file.write(seed_contents)
 
        # The seed file is missing or the records folder cannot be written.
        # The program still runs and starts with no records.
        except OSError:
            pass
 
    def load(self) -> pd.DataFrame | None:
        """Load all patient records. Return None if the file does not
        exist yet."""
        try:
            return pd.read_csv(self.__records_path)
        except FileNotFoundError:
            return None