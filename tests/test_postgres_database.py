import sys
from pathlib import Path

import psycopg

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app_test_factory import AppTestFactory
from data_manager.storage import PostgresDatabase


class TestPostgresDatabase:
    # ==========================================================
    # TEST 1 - DATABASE CANNOT BE REACHED
    # ==========================================================

    def test_database_down(self, monkeypatch):

        def fake_connect(url):
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
