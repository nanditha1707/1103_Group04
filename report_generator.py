import pandas as pd
 
 
class ReportGenerator:
    """Builds the daily reports from the patient records."""
 
    def __init__(
        self,
        records: pd.DataFrame,
        medicine_fields: list[str],
        route_labels: dict[str, str]
    ):
        self.__records = records
        # Record columns that hold the AI's medicines.
        self.__medicine_fields = medicine_fields
        # Maps each stored route value to its report label.
        self.__route_labels = route_labels

    def __count_medicines(self, date: str) -> pd.Series:
        """Return how many times each medicine was issued on a date."""
 
        # Filter to the selected date once.
        day_records = self.__records.loc[
            self.__records["date"] == date,
            self.__medicine_fields
        ]

        # Flatten all medicine columns into one Series, drop empties,
        # and count.
        return day_records.stack().value_counts()