
import pandas as pd
import os

COLUMN_DIAGNOSIS = "Title"   
COLUMN_CODE = "Code"       

def load_icd_dataset():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'icd_11.csv')

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"icd_11.csv not found at {csv_path}")

    df = pd.read_csv(csv_path)

    if COLUMN_DIAGNOSIS not in df.columns or COLUMN_CODE not in df.columns:
        raise ValueError(
            f"Expected columns '{COLUMN_DIAGNOSIS}' and '{COLUMN_CODE}' not found. "
            f"Actual columns: {df.columns.tolist()}"
        )

    return df