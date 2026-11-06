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