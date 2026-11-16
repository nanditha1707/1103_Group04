import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager.patients import QueryExporter


class TestQueryExport:
    # ==========================================================
    # TEST 1 - EXPORTED QUERY CSVS ARE DELETED
    # ==========================================================

    def test_clear_deletes_exported_queries(self, tmp_path):
        """
        Tests that clear deletes every exported query CSV and the empty
        query folder, so decrypted patient data does not stay on disk
        after the program exits.

        Expected:
        - export writes a CSV into the query folder.
        - clear removes the CSV and the now empty query folder.
        """

        query_dir = tmp_path / "query"
        export_time = datetime(2026, 11, 16, 9, 30)
        exporter = QueryExporter(query_dir, lambda: export_time)
        query_df = pd.DataFrame([{"name": "Alex Tan"}])

        exported = exporter.export(query_df)
        files_after_export = [path.name for path in query_dir.glob("*.csv")]
        exporter.clear()

        print("\nSCENARIO: Exported Query CSVs Are Deleted")
        print("Expected after export: ['query_20261116_093000.csv']")
        print("Expected after clear: query folder removed")
        print("Actual:", files_after_export, "|", query_dir.exists())

        assert exported is True
        assert files_after_export == ["query_20261116_093000.csv"]
        assert not query_dir.exists()
