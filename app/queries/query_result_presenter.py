import pandas as pd

from app import constants
from app.interfaces import PatientRecords, TableDisplay


class QueryResultPresenter:

    def __init__(
        self, tables: TableDisplay, records: PatientRecords
    ) -> None:
        self.__tables = tables
        self.__records = records

    def show(self, query_response: pd.DataFrame | None, not_found_error: str) -> str | None:
        error = None
        if query_response is None:
            error = constants.DATABASE_ERROR_MESSAGE
        elif query_response.empty:
            error = not_found_error
        else:
            # Wide results do not fit in the terminal, so they are
            # exported to a CSV instead of printed.
            if self.__tables.table_fits_screen(list(query_response.columns)):
                self.__tables.show_table(query_response)
            elif not self.__records.export_query(query_response):
                error = constants.EXPORT_FAILED_MESSAGE
        return error
