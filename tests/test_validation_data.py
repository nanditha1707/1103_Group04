import sys
from pathlib import Path

# allow this test file to import files from the main project folder
sys.path.append(
    str(Path(__file__).parent.parent)
)

# import the functions from validation_data.py
from validation_data import (
    load_icd_data,
    load_hsa_data,
    clean_icd_data,
    clean_hsa_data,
    get_cleaned_datasets
)


# ============================================================
# TEST 1 - LOAD ICD DATASET
# ============================================================

print("\nTEST 1 - LOAD ICD DATASET")
print("-------------------------")

# load the original ICD dataset
icd_df = load_icd_data()

# check if the file loaded successfully
if icd_df is not None:
    print("PASS - ICD dataset loaded successfully")
    print("Original ICD rows:", len(icd_df))

else:
    print("FAIL - ICD dataset could not be loaded")


# ============================================================
# TEST 2 - LOAD HSA DATASET
# ============================================================

print("\nTEST 2 - LOAD HSA DATASET")
print("-------------------------")

# load the original HSA dataset
hsa_df = load_hsa_data()

# check if the file loaded successfully
if hsa_df is not None:
    print("PASS - HSA dataset loaded successfully")
    print("Original HSA rows:", len(hsa_df))

else:
    print("FAIL - HSA dataset could not be loaded")


# ============================================================
# TEST 3 - CLEAN ICD DATASET
# ============================================================

print("\nTEST 3 - CLEAN ICD DATASET")
print("--------------------------")

# only continue if the ICD dataset loaded successfully
if icd_df is not None:

    # clean the ICD dataset
    cleaned_icd = clean_icd_data(icd_df)

    # display the column names after cleaning
    print("Cleaned ICD columns:")
    print(list(cleaned_icd.columns))

    # display number of rows after cleaning
    print("Rows after cleaning:", len(cleaned_icd))

    # display the first 5 cleaned rows
    print("\nFirst 5 cleaned ICD rows:")
    print(cleaned_icd.head())

    # check that the column was renamed correctly
    if list(cleaned_icd.columns) == ["DiseaseName"]:
        print("\nPASS - ICD columns cleaned correctly")

    else:
        print("\nFAIL - ICD columns are incorrect")


# ============================================================
# TEST 4 - CLEAN HSA DATASET
# ============================================================

print("\nTEST 4 - CLEAN HSA DATASET")
print("--------------------------")

# only continue if the HSA dataset loaded successfully
if hsa_df is not None:

    # clean the HSA dataset
    cleaned_hsa = clean_hsa_data(hsa_df)

    # expected columns after cleaning
    expected_columns = [
        "DrugName",
        "Dosage",
        "Strength",
        "ActiveIngredients",
        "ATCCode",
        "Classification"
    ]

    # display the column names after cleaning
    print("Cleaned HSA columns:")
    print(list(cleaned_hsa.columns))

    # display number of rows after cleaning
    print("Rows after cleaning:", len(cleaned_hsa))

    # display the first 5 cleaned rows
    print("\nFirst 5 cleaned HSA rows:")
    print(cleaned_hsa.head())

    # check that the columns were renamed correctly
    if list(cleaned_hsa.columns) == expected_columns:
        print("\nPASS - HSA columns cleaned correctly")

    else:
        print("\nFAIL - HSA columns are incorrect")


# ============================================================
# TEST 5 - CHECK MISSING VALUES
# ============================================================

print("\nTEST 5 - CHECK MISSING VALUES")
print("-----------------------------")

# check ICD dataset for missing disease names
if icd_df is not None:

    cleaned_icd = clean_icd_data(icd_df)

    # count missing disease names
    missing_icd = cleaned_icd[
        "DiseaseName"
    ].isnull().sum()

    print("ICD missing values:", missing_icd)

    if missing_icd == 0:
        print("PASS - No missing ICD disease names")

    else:
        print("FAIL - ICD still has missing disease names")


# check HSA dataset for missing values
if hsa_df is not None:

    cleaned_hsa = clean_hsa_data(hsa_df)

    # count all missing values in the cleaned HSA dataset
    missing_hsa = cleaned_hsa.isnull().sum().sum()

    print("HSA missing values:", missing_hsa)

    if missing_hsa == 0:
        print("PASS - No missing HSA values")

    else:
        print("FAIL - HSA still has missing values")


# ============================================================
# TEST 6 - CHECK DUPLICATES
# ============================================================

print("\nTEST 6 - CHECK DUPLICATES")
print("-------------------------")

# check ICD dataset for duplicate rows
if icd_df is not None:

    cleaned_icd = clean_icd_data(icd_df)

    icd_duplicates = cleaned_icd.duplicated().sum()

    print("ICD duplicate rows:", icd_duplicates)

    if icd_duplicates == 0:
        print("PASS - No ICD duplicates")

    else:
        print("FAIL - ICD still has duplicate rows")


# check HSA dataset for duplicate rows
if hsa_df is not None:

    cleaned_hsa = clean_hsa_data(hsa_df)

    hsa_duplicates = cleaned_hsa.duplicated().sum()

    print("HSA duplicate rows:", hsa_duplicates)

    if hsa_duplicates == 0:
        print("PASS - No HSA duplicates")

    else:
        print("FAIL - HSA still has duplicate rows")


# ============================================================
# TEST 7 - GET BOTH CLEANED DATASETS
# ============================================================

print("\nTEST 7 - GET CLEANED DATASETS")
print("-----------------------------")

# call the final function that returns both cleaned datasets
final_icd, final_hsa = get_cleaned_datasets()

# check that both datasets were returned
if final_icd is not None and final_hsa is not None:
    print("PASS - Both cleaned datasets returned")

    print("\nFinal ICD rows:", len(final_icd))
    print("Final HSA rows:", len(final_hsa))

    # display some final cleaned ICD data
    print("\nSample cleaned ICD data:")
    print(final_icd.head(5))

    # display some final cleaned HSA data
    print("\nSample cleaned HSA data:")
    print(final_hsa.head(5))

else:
    print("FAIL - Cleaned datasets were not returned")