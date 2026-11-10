# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
from datetime import datetime
import pandas as pd

import data_manager as data


# ======================================================================
# LOGIC MANAGER CLASS
# ======================================================================
class LogicManager:
    """Handles medicine classification, healthcare routing and
    queue number generation."""

    def __init__(self, hsa_df: pd.DataFrame | None):
        # Store the HSA dataset for medicine classification.
        self._hsa_df = hsa_df
