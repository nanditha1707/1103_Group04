import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import constants
from data_manager.dataset import HsaDataset, IcdDataset


class TestDatasetCleaning:
    # ==========================================================
    # TEST 1 - CLEAN ICD DATA
    # ==========================================================

    def test_clean_icd_data(self):

        fake_icd = pd.DataFrame({
            "Code": [
                " ca00 ",
                "CA00",
                "8A80",
                "CA02",
                "CA03"
            ],
            "Title": [
                " Acute nasopharyngitis ",
                "Acute nasopharyngitis",
                "Migraine",
                "",
                "-"
            ]
        })

        result = IcdDataset(constants.ICD_CSV_PATH).clean(fake_icd)

        print("\nSCENARIO: Clean ICD Data")
        print("Expected:")
        print("- Codes and names stripped and uppercased")
        print("- Duplicate Acute nasopharyngitis removed")
        print("- Empty value removed")
        print("- Dash value removed")
        print("- Migraine remains")
        print("Actual:")
        print(result)

        assert list(result["Code"]) == [
            "CA00",
            "8A80"
        ]
        assert list(result["DiseaseName"]) == [
            "ACUTE NASOPHARYNGITIS",
            "MIGRAINE"
        ]

    # ==========================================================
    # TEST 2 - CLEAN HSA DATA
    # ==========================================================

    def test_clean_hsa_data(self):

        fake_hsa = pd.DataFrame([
            {
                "Productname": " paracetamol ",
                "Dosageform": "Tablet",
                "Strength": "500mg",
                "Activeingredients": " paracetamol ",
                "ATCCode": "N02BE01",
                "Forensicclassification": "General Sale List"
            },
            {
                "Productname": " paracetamol ",
                "Dosageform": "Tablet",
                "Strength": "500mg",
                "Activeingredients": " paracetamol ",
                "ATCCode": "N02BE01",
                "Forensicclassification": "General Sale List"
            }
        ])

        result = HsaDataset(constants.HSA_CSV_PATH).clean(fake_hsa)

        print("\nSCENARIO: Clean HSA Data")
        print("Expected Drug Name: PARACETAMOL")
        print("Expected Active Ingredient: PARACETAMOL")
        print("Expected Rows: 1")
        print("Actual:")
        print(result)

        assert len(result) == 1
        assert result.iloc[0]["DrugName"] == "PARACETAMOL"
        assert result.iloc[0]["ActiveIngredients"] == "PARACETAMOL"
