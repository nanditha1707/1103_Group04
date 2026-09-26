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

# Clean ICD Dataset
def clean_icd_data(icd_df):

    # Remove the columns that are completely empty
    icd_df = icd_df.dropna( 
        axis=1,
        how="all",
        # inplace=True
    ) 

    # Catch all empty strings
    icd_df = icd_df.replace( 
        r'^\s*$', 
        np.nan, 
        regex=True
    )

    # Remove all duplicate rows
    icd_df = icd_df.drop_duplicates()

    return icd_df 

# Clean HSA Dataset
def clean_hsa_data(hsa_df):

    # Remove the columns that are completely empty
    hsa_df = hsa_df.dropna(
        axis=1,
        how="all",
        # inplace=True
    )

    # Catch all empty strings
    hsa_df = hsa_df.replace( 
        r'^\s*$', 
        np.nan, 
        regex=True
    )

     # Remove all duplicate rows
    hsa_df = hsa_df.drop_duplicates()

    # Convert date to date time
    hsa_df['Approvaldate'] = pd.to_datetime(
        hsa_df['Approvaldate'],
        errors='coerce'
    )

    # Convert date time to YYYY/MM/DD
    hsa_df["Approvaldate"] = (
        hsa_df["Approvaldate"]
        .dt.strftime("%Y/%m/%d")
    )

    return hsa_df 

