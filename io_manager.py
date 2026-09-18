# prompt user for information

input
def input_values():
    consent = input("Please enter your consent to share your data with the AI pharmacist (yes/no):")
    patient_name = input("Please enter your full name exactly as it appears on your passport: ")
    patient_age = input("Please enter your age:")
    patient_gender = input("Please enter your gender (M/F):")
    patient_Chronic_conditions = input("Do you have any chronic conditions?[Hypertension/Diabetes/High cholesterol/Chronic obstructive pulmonary disease](Y/N)")
    patient_Current_medications = input("Please let us know if you are currently on any medications(Y/N):")
    patient_Current_symptoms = input("Please let us know what are your current symptoms:")
    patient_number = input("Please enter your phone number (+65): ")

