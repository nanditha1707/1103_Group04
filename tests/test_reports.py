import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import DataManagerFactory
from fakes import FakeDatabase


class TestReports:
    def test_medicine_count(self):

        # COUNT(*) returns one row with one value.
        database = FakeDatabase([(2,)])
        data = DataManagerFactory.create(database)

        result = data.get_medicine_count(
            "PARACETAMOL",
            "2026-10-14"
        )

        print("\nSCENARIO: Specific Medicine Count")
        print("Medicine: PARACETAMOL")
        print("Expected: {'PARACETAMOL': 2}")
        print("Actual:", result)

        assert result == {"PARACETAMOL": 2}
        assert database.fetched_parameters == [("2026-10-14", "PARACETAMOL")]

    def test_medicine_not_issued(self):

        data = DataManagerFactory.create(FakeDatabase([(0,)]))

        result = data.get_medicine_count(
            "IBUPROFEN",
            "2026-10-14"
        )

        print("\nSCENARIO: Medicine Not Issued")
        print("Expected: {}")
        print("Actual:", result)

        assert result == {}

    def test_medicine_breakdown(self):

        database = FakeDatabase([
            ("PARACETAMOL", 2),
            ("CETIRIZINE", 1),
            ("IBUPROFEN", 1)
        ])
        data = DataManagerFactory.create(database)

        result = data.get_medicine_breakdown(
            "2026-10-14"
        )

        print("\nSCENARIO: Medicine Breakdown")
        print("Expected:")
        print("PARACETAMOL = 2")
        print("IBUPROFEN = 1")
        print("CETIRIZINE = 1")
        print("Actual:")
        print(result)

        assert result["PARACETAMOL"] == 2
        assert result["IBUPROFEN"] == 1
        assert result["CETIRIZINE"] == 1
        assert database.fetched_parameters == [("2026-10-14",)]

    def test_patient_type_breakdown(self):

        data = DataManagerFactory.create(FakeDatabase([
            ("Retail", 1),
            ("Doctor", 1),
            ("Pharmacist", 1)
        ]))

        result = data.get_patient_type_breakdown(
            "2026-10-14"
        )

        print("\nSCENARIO: Patient Type Breakdown")
        print("Expected:")
        print("Doctor = 1")
        print("Pharmacy = 1")
        print("Retail = 1")
        print("Actual:")
        print(result)

        # Labels follow the order of ROUTE_LABELS, not the database order.
        assert list(result) == ["Doctor", "Pharmacy", "Retail"]
        assert result["Doctor"] == 1
        assert result["Pharmacy"] == 1
        assert result["Retail"] == 1

    def test_reports_database_down(self):

        data = DataManagerFactory.create(FakeDatabase(None))

        print("\nSCENARIO: Database Cannot Be Reached")
        print("Expected: None from every report")

        assert data.get_medicine_count("PARACETAMOL", "2026-10-14") is None
        assert data.get_medicine_breakdown("2026-10-14") is None
        assert data.get_patient_type_breakdown("2026-10-14") is None
