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

    # Keep only the disease title column
    icd_df = icd_df[
        [
            "Title"
        ]
    ].copy()


    # Rename column to make it clearer
    icd_df = icd_df.rename(
        columns={
            "Title": "DiseaseName"
        }
    )


    # Replace empty strings with NaN
    icd_df = icd_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )


    # Replace dash values with NaN
    icd_df = icd_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


    # Remove rows where disease name is missing
    icd_df = icd_df.dropna(
        subset=[
            "DiseaseName"
        ]
    )

    # Remove extra spaces
    icd_df["DiseaseName"] = (
        icd_df["DiseaseName"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicate diseases
    icd_df = icd_df.drop_duplicates()

    # Reset index
    icd_df = icd_df.reset_index(
        drop=True
    )


    return icd_df

# Clean HSA Dataset
def clean_hsa_data(hsa_df):

    # Keep only the required columns
    hsa_df = hsa_df[
        [
            "Productname",
            "Dosageform",
            "Strength",
            "Activeingredients",
            "ATCCode",
            "Forensicclassification"
        ]
    ].copy()


    # Rename columns to clearer names
    hsa_df = hsa_df.rename(
        columns={
            "Productname": "DrugName",
            "Dosageform": "Dosage",
            "Strength": "Strength",
            "Activeingredients": "ActiveIngredients",
            "ATCCode": "ATCCode",
            "Forensicclassification": "Classification"
        }
    )


    # Replace empty strings with NaN
    hsa_df = hsa_df.replace(
        r"^\s*$",
        np.nan,
        regex=True
    )

    # Replace dash values with NaN
    hsa_df = hsa_df.replace(
        r"^\s*[-–—]+\s*$",
        np.nan,
        regex=True
    )


    # Remove rows that are missing important information
    hsa_df = hsa_df.dropna(
        subset=[
            "DrugName",
            "Dosage",
            "Strength",
            "ActiveIngredients",
            "ATCCode",
            "Classification"
        ]
    )

    # Remove extra spaces
    hsa_df["DrugName"] = (
        hsa_df["DrugName"]
        .astype(str)
        .str.strip()
    )

    hsa_df["Dosage"] = (
        hsa_df["Dosage"]
        .astype(str)
        .str.strip()
    )

    hsa_df["Strength"] = (
        hsa_df["Strength"]
        .astype(str)
        .str.strip()
    )

    hsa_df["ActiveIngredients"] = (
        hsa_df["ActiveIngredients"]
        .astype(str)
        .str.strip()
    )

    hsa_df["ATCCode"] = (
        hsa_df["ATCCode"]
        .astype(str)
        .str.strip()
    )

    hsa_df["Classification"] = (
        hsa_df["Classification"]
        .astype(str)
        .str.strip()
    )

    # Remove duplicate rows
    hsa_df = hsa_df.drop_duplicates()

    # Reset index
    hsa_df = hsa_df.reset_index(
        drop=True
    )

    return hsa_df 

#Load the datasets
def get_cleaned_datasets():

    icd_df = load_icd_data()
    hsa_df = load_hsa_data()

    if icd_df is None or hsa_df is None:
        return None, None

    icd_df = clean_icd_data(
        icd_df
    )

    hsa_df = clean_hsa_data(
        hsa_df
    )

    return icd_df, hsa_df

