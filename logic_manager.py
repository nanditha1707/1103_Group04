from datetime import datetime

# get all the medicine names from the AI output
def get_medicines(ai_output): 
    medicines = []

    # keys where the medicines are stored in the AI output
    medicine_keys =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2", 
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # go through each medicine key
    for key in medicine_keys:

        # get the medicine stored under the key
        medicine = ai_output.get(key)

        # only add it if there is an medicine
        if medicine:
            medicines.append(medicine)

    # return the list of medicines
    return medicines

# get HSA classification of medicine
def get_classification(medicine, hsa_df):

    # go through every row in the HSA dataset
    for index, row in hsa_df.iterrows():

        # convert the drug name to lowercase
        drug_name= str(row["DrugName"]).lower() 

        # Concert the active ingredient to lowercase
        ingredient= str(row["ActiveIngredients"]).lower() 

        # check if the AI medicine matches either field
        if medicine.lower() in drug_name or medicine.lower() in ingredient:

            # return the HSA classification
            return row["Classification"]

    # return none id medicine is not fouind
    return None

