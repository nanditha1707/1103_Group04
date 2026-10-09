# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import pandas as pd

FILE_PATH_ICD11 = "icd_11.csv"
FILE_PATH_HSA = "hsa.csv"


df1 = pd.read_csv(FILE_PATH_ICD11)
df2 = pd.read_csv(FILE_PATH_HSA)

# this is the dictionary output of our AI API
# currently as a placeholder
ai_output = {
    "primary_diagnosis_ICD11_Title": "Viral encephalitis, not elsewhere classified",
    "primary_diagnosis_ICD11_Code": "1C80",
    "secondary_diagnosis_ICD11_Title": "Viral encephalitis, not elsewher classified",
    "secondary_diagnosis_ICD11_Code": "1C0",
    "primary_diagnosis_medicine_1": "Oseltamivir",
    "primary_diagnosis_medicine_2": "Paracetamol",
    "secondary_diagnosis_medicine_1": "Dextromethorphan",
    "secondary_diagnosis_medicine_2": "Chlorpheniramine",
    "ai_confidence_score": 85,
    "refused": "false",
}

# ======================================================================
# VALIDATE DIAGNOSIS, CODE AND MEDICINE
# ======================================================================

# Two series with the column names "Title" and "Code" 
# is pulled from the ICD11 dataset.
dataset_diagnosis = df1["Title"].str.lower()
dataset_code = df1["Code"].str.lower()

# The pandas series with the column name "Productname" 
# is pulled from the HSA medicine dataset.
dataset_medicine = df2["Productname"].str.lower()

def validate_diagnosis_code(diagnosis: str, code: str, label: str) -> bool:
    """The validate_diagnosis_code() function stores the input of 
    three string values named diagnosis, code and label (diagnosis) 
    represent the dictionary(ai_output) value of the diagnosis
    (code) represents the dictionary(ai_output) value of the code 
    (label) represents the level(primary/secondary) of the output 
    Additionally, the result of which output is in the dataset 
    and/or which output is not in the dataset is printed."""

    # False boolean value remains in isvalid_code unless the ai_output 
    # code value finds a match in the "Code" column of df1.
    isvalid_code = False

    for valid_code in dataset_code:
        if code.lower() == valid_code.lower():
            isvalid_code = True
            break

    # False boolean value remains in isvalid_diagnosis unless the 
    # ai_output value finds a match in the "Title" column of df1.
    isvalid_diagnosis = False

    for valid_diagnosis in dataset_diagnosis:
       if diagnosis.lower() == valid_diagnosis.lower():
            isvalid_diagnosis = True
            break

    # Prints the result of a valid match.
    # Else it will indicate which specific data is not found.
    if isvalid_code and isvalid_diagnosis:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are found in the dataset.")
    elif isvalid_diagnosis:
        print(f"The {label} diagnosis: '{diagnosis}' is found in the dataset but the {label} code: '{code}' is not found.")
    elif isvalid_code:
        print(f"The {label} code: '{code}' is found in the dataset but the {label} diagnosis: '{diagnosis}' is not found.")
    else:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are not found in the dataset.")

    return isvalid_code, isvalid_diagnosis


def validate_medicine(medicine: str, label: str) -> bool:
    """
    This function has the same concept as validate_diagnosis_code() 
    function but it is to validate medicine instead of disease."""

    isvalid_medicine = False

    # If AI output medicine is in the dataset then set isvalid_medicine
    # flag to True. Else it stays as False.
    for valid_medicine in dataset_medicine:
        if medicine.lower() == valid_medicine.lower():
            isvalid_medicine = True
            break
    
    if isvalid_medicine:
        print(f"The {label} medicine: '{medicine}' is found in the dataset.")
    else:
        print(f"The {label} medcine: '{medicine}'is not found in the dataset.")

    return isvalid_medicine
