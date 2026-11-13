QUIT_SIGNAL = -99
ADMIN_PASSWORD = "Password"
MENU_EXIT_MESSAGE = "Admin Password Inputted, Exiting Program Now!"
DATABASE_ERROR_MESSAGE = "The patient records database could not be reached, please try again later!"
INVALID_OPTION_NUMBER_MESSAGE = "This is not a valid option number!"

MAIN_MENU_OPTIONS = [
    "1. Patient Registration",
    "2. Healthcare Professional Portal",
    "3. Exit"
]

HEALTHCARE_PORTAL_OPTIONS = [
    "1. Query Current Patient Information",
    "2. Query Past Patient Information",
    "3. Reports"
]

CURRENT_PATIENT_QUERY_LABEL = "Query Current Patient Information"
PAST_PATIENT_QUERY_LABEL = "Query Past Patient Information"
DATE_PROMPT = "Enter the Date here. (YYYY-MM-DD): "

FILTER_OPTIONS = [
    "1. Patient Information",
    "2. Medical Information",
    "3. AI Ouput Information",
    "4. All Records"
]

# Asked after the filter: look up one patient, or every patient on the date.
SINGLE_PATIENT_LABEL = "One Patient (by Queue Number)"
ALL_PATIENTS_LABEL = "All Patients on This Date"
QUEUE_NUMBER_PROMPT = "Enter the Patient's Queue Number here: "
PATIENT_NOT_FOUND_MESSAGE = "There is no such patient, please enter a valid queue number!"
NO_PATIENTS_ON_DATE_MESSAGE = "There are no patient records for this date!"

EXPORT_FAILED_MESSAGE = "The query results could not be exported!"

MEDICINE_COUNT_LABEL = "Specific Medicine Count"
MEDICINE_BREAKDOWN_LABEL = "Medicine Breakdown"
PATIENT_TYPE_BREAKDOWN_LABEL = "Patient Type Breakdown"
MEDICINE_COUNT_HEADER = ""
MEDICINE_BREAKDOWN_HEADER = "Medicine Breakdown Report"
PATIENT_TYPE_BREAKDOWN_HEADER = "Patient Type Breakdown Report"
MEDICINE_PROMPT = "Enter a medicine name: "

RECORD_SAVE_FAILED_MESSAGE = ("The program has encountered an error. "
                              "Please approach a nurse or clerk for manual registration.\n"
                              "Error: {error}")
