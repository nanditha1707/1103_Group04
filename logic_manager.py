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

# to decide where the patient should be routed to
def decide_route(all_user_responses, ai_output, hsa_df):

    # AI bypass always routes the patient to a doctor
    if all_user_responses.get("ai_bypass")==True:
        return "Doctor"

    # get all medicines reccomended by AI
    medicines=get_medicines(ai_output)

    # remember if at least one pharm only medicine is found
    pharmacist_needed = False

    # check each recommended medicine
    for medicine in medicines:

        # get the medicine classification from HSA data
        classification =get_classification(
            medicine,
            hsa_df
        )

        # prescription only medicine requires doctor
        if classification=="Prescription Only":
            return "Doctor"

        # pharmacy only medicine requires pharmacist
        elif classification=="Pharmacy Only":
            pharmacist_needed=True

    #if no prescription medicine but a pharmacy only medicine was found
    if pharmacist_needed:
        return "Pharmacist"

    # otherwise patient can go to retail
    return "Retail"