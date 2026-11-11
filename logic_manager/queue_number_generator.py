import pandas as pd

from .route import Route

class QueueNumberGenerator:
    """
    Gives out the next queue number for a date, e.g. D008, by checking
    the saved patient records.
    """

    # Letter at the start of each queue number to differentiate.
    _PREFIXES = {
        Route.EMERGENCY: "U",
        Route.DOCTOR: "D",
        Route.PHARMACIST: "P",
        Route.RETAIL: "PR"
    }

    def __init__(self, records_csv_path: str):
        self.__records_csv_path = records_csv_path

    def next_number(self, route: Route, date: str) -> str | None:
        """
        Return the next queue number for the route on the given date, e.g. D008.
        """

        prefix = self._PREFIXES.get(route)

        # Initialise the highest_number variable.
        # Meant to store the highest prefix queue number for the day.
        highest_number = 0

        for existing_queue_number in self._read_queue_numbers(date):
            number = self._parse_number(existing_queue_number, prefix)

            # Keep the highest number.
            if number is not None and number > highest_number:
                highest_number = number

        # :03d sets the minimum width to 3, so instead of D9 it is D009.
        return f"{prefix}{highest_number + 1:03d}"

    @staticmethod
    def _parse_number(queue_number: str, prefix: str) -> int | None:
        """
        Returns the highest number related to the prefix.
        Returns None if the queue number belongs to another queue or is corrupted.
        """

        # Only look at queue numbers in the same queue e.g. D001.
        if not queue_number.startswith(prefix):
            return None

        try:
            # [len(prefix):] drops the letter e.g. "D007" -> "007".
            # int() turns "007" into 7.
            return int(queue_number[len(prefix):])

        # Skip queue numbers that are corrupted.
        except ValueError:
            return None


    def _read_queue_numbers(self, date: str) -> list[str]:
        """
        Return every queue number saved on the given date. 
        Returns an empty list if there are no usable records, so the queue startsfrom 0.
        """
        try:
            # dtype=str keeps queue numbers like D001 as text.
            # keep_default_na=False turns blank cells into "" instead of NaN.
            records_df = pd.read_csv(
                self.__records_csv_path,
                dtype=str,
                keep_default_na=False
            )

            # Only look at the patients from this date.
            return list(records_df[records_df["date"] == date]["queue_number"])

        # Placeholder error catcher as e
        except Exception as e:
            return []
