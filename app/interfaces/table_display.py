from collections.abc import Mapping
from typing import Protocol

import pandas as pd


class TableDisplay(Protocol):

    def show_table(self, report: pd.DataFrame | Mapping[str, object], title: str = "") -> None:
        pass

    def table_fits_screen(self, columns: list[str]) -> bool:
        pass
