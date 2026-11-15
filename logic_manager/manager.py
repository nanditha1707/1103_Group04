from collections.abc import Callable
from datetime import datetime

from .queue_number_generator import QueueNumberGenerator
from .router import Router

class LogicManager:
    """
    Handles medicine classification, healthcare routing and
    queue number generation.

    LogicManagerFactory gives it every object it needs and it creates none
    itself, so a test can pass in fakes and a fixed clock.
    """

    # Formats used for the date and time in the result.
    __DATE_FORMAT = "%Y-%m-%d"
    __TIME_FORMAT = "%H:%M:%S"

    def __init__(
        self, router: Router, queue_generator: QueueNumberGenerator, clock: Callable[[], datetime]
    ):
        self.__router = router
        self.__queue_generator = queue_generator
        self.__clock = clock

    def process_result(self, ai_output: dict) -> dict:
        """
        Create the final domain result. Routes the patient, gives them a
        queue number and returns both with the current date and time.
        """

        # Where the patient goes.
        route = self.__router.decide(ai_output)

        now = self.__clock()
        today = now.strftime(self.__DATE_FORMAT)

        current_time = now.strftime(self.__TIME_FORMAT)

        queue_number = self.__queue_generator.next_number(route, today)

        return {
            "queue_number": queue_number,
            "date": today,
            "time": current_time,
            "route": route.value
        }