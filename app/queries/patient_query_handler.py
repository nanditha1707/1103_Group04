from collections.abc import Sequence

from app.interfaces import UserPrompt

from .query_filter import QueryFilter
from .query_result_presenter import QueryResultPresenter
from .query_scope import QueryScope


class PatientQueryHandler:

    def __init__(
        self, prompt: UserPrompt, filters: Sequence[QueryFilter], scopes: Sequence[QueryScope], presenter: QueryResultPresenter
    ) -> None:
        self.__prompt = prompt
        self.__filters = list(filters)
        self.__scopes = list(scopes)
        self.__presenter = presenter

    def handle(self, date: str) -> str | None:
        query_filter = self.__prompt.choose(self.__filters)
        if query_filter is None:
            return None

        # Both options query the database directly, so patients
        # registered by other users are found too.
        scope = self.__prompt.choose(self.__scopes)
        if scope is None:
            return None

        return self.__presenter.show(scope.fetch(query_filter.columns, date), scope.not_found_error)
