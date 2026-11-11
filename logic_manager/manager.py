from datetime import datetime
import pandas as pd

import data_manager as data

class LogicManager:
    """
    Handles medicine classification, healthcare routing and
    queue number generation.
    """

    # Formats used for the date and time in the result.
    _DATE_FORMAT = "%Y-%m-%d"
    _TIME_FORMAT = "%H:%M:%S"

    def __init__(
            self,
            hsa_df: pd.DataFrame | None,
            records_csv_path: str = data.RECORDS_CSV_PATH
        ):
            # The records path is passed in instead of being looked up inside, 
            # so a test or a different storage location can be used without changing code.
            self.__router = Router(hsa_df)
            self.__queue_generator = QueueNumberGenerator(records_csv_path)

    def process_result(self, ai_output: dict) -> dict:
        """
        Create the final domain result. Routes the patient, gives them a
        queue number and returns both with the current date and time.
        """

        # Where the patient goes.
        route = self.__router.decide(ai_output)

        now = datetime.now()
        today = now.strftime(self._DATE_FORMAT)

        if route is None:
            queue_number = None
        else:
            queue_number = self.__queue_generator.next_number(route, today)

        return {
            "queue_number": queue_number,
            "date": today,
            "time": now.strftime(self._TIME_FORMAT),
            "route": route.value if route is not None else None
        }