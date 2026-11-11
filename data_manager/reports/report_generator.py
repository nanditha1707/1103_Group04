from data_manager.storage import RecordCounter


class ReportGenerator:
    """Builds the daily reports from the patient records."""

    def __init__(
        self, counter: RecordCounter, route_labels: dict[str, str]
    ):
        self.__counter = counter
        # Maps each stored route value to its report label.
        self.__route_labels = route_labels

# ======================================================================
# REPORT FUNCTIONS
# ======================================================================
    def get_medicine_count(self, medicine: str, date: str) -> dict[str, int] | None:
        """Return a dict with how many times a specific medicine was
        issued on a given date. Returns an empty dict if it was not
        issued."""

        times_issued = self.__counter.count_medicine(medicine, date)
        if times_issued is None:
            return None

        if times_issued == 0:
            return {}

        return {medicine: times_issued}

    def get_medicine_breakdown(self, date: str) -> dict[str, int] | None:
        """Return a dict of each medicine issued on a given date and how
        many times it was issued."""

        return self.__counter.count_each_medicine(date)

    def get_patient_type_breakdown(self, date: str) -> dict[str, int] | None:
        """Return how many Emergency, Doctor, Pharmacy and Retail
        patients there were on a given date."""

        route_counts = self.__counter.count_each_route(date)
        if route_counts is None:
            return None

        # Put the label and matching value into the dictionary,
        # ignoring any entries with no value.
        patient_types = {}
        for route, label in self.__route_labels.items():
            if route in route_counts:
                patient_types[label] = route_counts[route]

        return patient_types
