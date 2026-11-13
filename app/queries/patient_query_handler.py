from collections.abc import Sequence

from app import constants
from data_manager import DataManager
from io_manager import IOManager

from .query_result_presenter import QueryResultPresenter
from .query_scope import QueryScope


class PatientQueryHandler:

    def __init__(
        self, io: IOManager, data: DataManager, scopes: Sequence[QueryScope], presenter: QueryResultPresenter
    ) -> None:
        self.__io = io
        self.__data = data
        self.__scopes = list(scopes)
        self.__presenter = presenter

    def handle(self, date: str) -> str | None:
        filter_option = self.__io.prompt_menu(constants.FILTER_OPTIONS)
        error = self.__io.validate_option(filter_option, len(constants.FILTER_OPTIONS))
        if error is not None:
            return error

        filter_columns = self.__data.get_patient_filter(filter_option)
        if filter_columns is None:
            return constants.INVALID_FILTER_MESSAGE

        # Both options query the database directly, so patients
        # registered by other users are found too.
        scope = self.__io.choose(self.__scopes)
        if scope is None:
            return None

        return self.__presenter.show(scope.fetch(filter_columns, date), scope.not_found_error)
