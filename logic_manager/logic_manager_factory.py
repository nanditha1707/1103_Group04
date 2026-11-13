from datetime import datetime

import pandas as pd

from data_manager.constants import SGT

from .manager import LogicManager
from .medicine_classifier import MedicineClassifier
from .queue_number_generator import QueueNumberGenerator
from .queue_number_source import QueueNumberSource
from .router import Router


class LogicManagerFactory:
    """
    Builds the LogicManager that main.py uses.

    This is the only class that creates logic_manager's concrete classes.
    LogicManager and Router are given the objects they need instead so
    each one can be swapped or faked without changing the others.
    """

    @staticmethod
    def create(hsa_df: pd.DataFrame | None, queue_numbers: QueueNumberSource) -> LogicManager:
        """
        Return a LogicManager that routes with the cleaned HSA dataset and
        asks queue_numbers for the highest queue number given out so far.

        hsa_df can be None if it failed to load. Router then gets no
        MedicineClassifier and sends every non-emergency patient to a doctor.
        """
        if hsa_df is None:
            classifier = None
        else:
            classifier = MedicineClassifier(hsa_df)

        return LogicManager(
            Router(classifier),
            QueueNumberGenerator(queue_numbers),
            lambda: datetime.now(SGT)
        )
