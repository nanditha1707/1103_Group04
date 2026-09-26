import pandas as pd
import numpy as np
from pathlib import Path

# Import filepaths
base_dir= Path(__file__).parent  # find the directory path of the folder containing the currently running script.
dataset_dir= base_dir/ "datasets"

icd_file = dataset_dir / "icd_11.csv"
hsa_file = dataset_dir / "ListingofRegisteredTherapeuticProducts.csv"

# Load ICD Dataset
def load_icd_data():

    try:
        icd_df = pd.read_csv(
            icd_file,
            low_memory=False
        )

        return icd_df

    except FileNotFoundError:
        return None

    except pd.errors.ParserError:
        return None

# Load HSA Dataset
def load_hsa_data():

    try:
        hsa_df = pd.read_csv(
            hsa_file,
            low_memory=False
        )

        return hsa_df

    except FileNotFoundError:
        return None
    
    except pd.errors.ParserError:
        return None

