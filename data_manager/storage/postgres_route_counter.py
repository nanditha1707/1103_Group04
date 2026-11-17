from psycopg import sql

from .database import Database
from .route_counter import RouteCounter


class PostgresRouteCounter(RouteCounter):
    """Counts the patients on each route straight from the records table,
    since the route column is not encrypted."""

    def __init__(
        self, database: Database, table_name: str
    ):
        self.__database = database
        self.__table = sql.Identifier(table_name)

    def count_each_route(self, date: str) -> dict[str, int] | None:
        sql_statement = sql.SQL("""
            SELECT route, COUNT(*)
            FROM {}
            WHERE date = %s
            GROUP BY route
        """).format(self.__table)
        rows = self.__database.fetch_rows(sql_statement, (date,))
        if rows is None:
            return None

        # Each row is (route, count).
        return dict(rows)
