MAIN_MENU_HEADER = "Main Menu"
REGISTRATION_LABEL = "Patient Registration"
HEALTHCARE_PORTAL_LABEL = "Healthcare Professional Portal"
EXIT_LABEL = "Exit"

ADMIN_PASSWORD = "Password"
EXIT_CODE_PROMPT = "Enter the exit code here: "
MENU_EXIT_MESSAGE = "Admin Password Inputted, Exiting Program Now!"
WRONG_PASSWORD_MESSAGE = "This is not the right password!"

RECORD_SAVE_FAILED_MESSAGE = ("The program has encountered an error. "
                              "Please approach a nurse or clerk for manual registration.\n"
                              "Error: {error}")

STARTUP_FAILED_MESSAGE = ("The program could not start: {error}\n"
                          "Please check PATIENT_DATA_ENCRYPTION_KEY in the .env file.")

CURRENT_PATIENT_QUERY_LABEL = "Query Current Patient Information"
PAST_PATIENT_QUERY_LABEL = "Query Past Patient Information"
REPORTS_LABEL = "Reports"
DATE_PROMPT = "Enter the Date here. (YYYY-MM-DD): "
DATABASE_ERROR_MESSAGE = "The patient records database could not be reached, please try again later!"

PATIENT_INFO_FILTER_LABEL = "Patient Information"
MEDICAL_INFO_FILTER_LABEL = "Medical Information"
AI_OUTPUT_FILTER_LABEL = "AI Output Information"
ALL_RECORDS_FILTER_LABEL = "All Records"

# Column groups shown by each healthcare portal query filter option.
PATIENT_COLUMNS = [
    "name",
    "nric",
    "gender",
    "birthdate",
    "age",
    "phone_number"
]

MEDICAL_COLUMNS = [
    "date",
    "route",
    "pregnancy",
    "current_symptoms",
    "symptom_onset_days",
    "chronic_conditions",
    "current_medications",
    "drug_allergies"
]

AI_OUTPUT_COLUMNS = [
    "primary_diagnosis_ICD11_Code",
    "primary_diagnosis_ICD11_Title",
    "primary_diagnosis_explanation",
    "primary_diagnosis_medicine_1",
    "primary_diagnosis_medicine_2",
    "secondary_diagnosis_ICD11_Code",
    "secondary_diagnosis_ICD11_Title",
    "secondary_diagnosis_explanation",
    "secondary_diagnosis_medicine_1",
    "secondary_diagnosis_medicine_2",
    "ai_confidence_score"
]

# Asked after the filter: look up one patient, or every patient on the date.
SINGLE_PATIENT_LABEL = "One Patient (by Queue Number)"
ALL_PATIENTS_LABEL = "All Patients on This Date"
QUEUE_NUMBER_PROMPT = "Enter the Patient's Queue Number here: "
PATIENT_NOT_FOUND_MESSAGE = "There is no such patient, please enter a valid queue number!"
NO_PATIENTS_ON_DATE_MESSAGE = "There are no patient records for this date!"
EXPORT_FAILED_MESSAGE = "The query results could not be exported!"

REPORT_MENU_HEADER = "Reports"
MEDICINE_COUNT_LABEL = "Specific Medicine Count"
MEDICINE_BREAKDOWN_LABEL = "Medicine Breakdown"
PATIENT_TYPE_BREAKDOWN_LABEL = "Patient Type Breakdown"
MEDICINE_COUNT_HEADER = ""
MEDICINE_BREAKDOWN_HEADER = "Medicine Breakdown Report"
PATIENT_TYPE_BREAKDOWN_HEADER = "Patient Type Breakdown Report"
MEDICINE_PROMPT = "Enter a medicine name: "
NO_MATCHING_RECORDS_MESSAGE = "There is no matching records for the given date!"
