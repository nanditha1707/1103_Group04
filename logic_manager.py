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

