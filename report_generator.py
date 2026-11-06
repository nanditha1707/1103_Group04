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

    def get_medicine_count(self, medicine: str, date: str) -> dict[str, int]:
        """Return a dict with how many times a specific medicine was
        issued on a given date. Returns an empty dict if it was not
        issued."""
 
        medicine_counts = self.__count_medicines(date)
 
        # Keep only the requested medicine, if it appears at all.
        if medicine in medicine_counts.index:
            return {medicine: int(medicine_counts[medicine])}
 
        return {}

    def get_medicine_breakdown(self, date: str) -> dict:
        """Return a dict of each medicine issued on a given date and how
        many times it was issued."""
 
        # Returns medicine counts as a dictionary.
        return self.__count_medicines(date).to_dict()