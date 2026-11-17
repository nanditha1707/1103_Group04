import sys
from pathlib import Path
from typing import NoReturn

import psycopg
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app_test_factory import AppTestFactory
from data_manager.storage import PostgresDatabase


class TestPostgresDatabase:
    # ==========================================================
    # TEST 1 - DATABASE CANNOT BE REACHED
    # ==========================================================

    def test_database_down(self, monkeypatch: pytest.MonkeyPatch):

        def fake_connect(url: str) -> NoReturn:
            raise psycopg.OperationalError("connection refused")

        monkeypatch.setattr(
            psycopg,
            "connect",
            fake_connect
        )

        database = PostgresDatabase("postgresql://unreachable")
        data = AppTestFactory.create_data_manager(database)

        fetch_result = database.fetch_rows(
            "SELECT 1",
            ()
        )
        query_result = data.get_patient_by_queue(
            "D001",
            ["name"],
            "2026-10-14"
        )
        export_result = data.export_record(
            {"name": "Charlie Ng"},
            {},
            {"queue_number": "D001"}
        )

        print("\nSCENARIO: Database Cannot Be Reached")
        print("Expected fetch_rows: None")
        print("Expected get_patient_by_queue: None")
        print("Expected export_record: an error message")
        print("Actual:", fetch_result, "|", query_result, "|", export_result)

        assert fetch_result is None
        assert query_result is None
        assert "connection refused" in export_result

    # ==========================================================
    # TEST 2 - DATABASE URL IS MISSING
    # ==========================================================

    def test_missing_database_url(self):
        """
        Check that a missing or empty POSTGRESQL_CLOUD_DATABASE_URL does not
        crash the program.

        Steps:
        1. Make one PostgresDatabase with no URL (None), as if the variable
           is not in the .env file, and one with an empty URL ("").
        2. Run fetch_rows and execute on each.

        Expected:
        - fetch_rows returns None.
        - execute returns a message saying no database URL was given.
        """

        for database_url in (None, ""):
            database = PostgresDatabase(database_url)

            fetch_result = database.fetch_rows("SELECT 1", ())
            execute_result = database.execute("SELECT 1", {})

            print("\nSCENARIO: Database URL Is Missing")
            print("URL:", repr(database_url))
            print("Expected: None | a message saying no database URL was given")
            print("Actual:", fetch_result, "|", execute_result)

            assert fetch_result is None
            assert execute_result is not None
            assert "no database URL was given" in execute_result

    # ==========================================================
    # TEST 3 - DATABASE URL IS INVALID
    # ==========================================================

    def test_invalid_database_url(self):
        """
        Check that a badly formatted POSTGRESQL_CLOUD_DATABASE_URL does not
        crash the program.

        Steps:
        1. Make a PostgresDatabase with the URL "not-a-url".
        2. Run fetch_rows and execute on it. psycopg rejects the URL
           before it tries to connect, so no network is needed.

        Expected:
        - fetch_rows returns None.
        - execute returns psycopg's ProgrammingError message.
        """

        database = PostgresDatabase("not-a-url")

        fetch_result = database.fetch_rows("SELECT 1", ())
        execute_result = database.execute("SELECT 1", {})

        print("\nSCENARIO: Database URL Is Invalid")
        print("Expected: None | a ProgrammingError message")
        print("Actual:", fetch_result, "|", execute_result)

        assert fetch_result is None
        assert execute_result is not None
        assert "ProgrammingError" in execute_result
