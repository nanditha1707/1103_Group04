QUIT_SIGNAL = -99
ADMIN_PASSWORD = "Password"
MENU_EXIT_MESSAGE = "Admin Password Inputted, Exiting Program Now!"
DATABASE_ERROR_MESSAGE = "The patient records database could not be reached, please try again later!"

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

FILTER_OPTIONS = [
    "1. Patient Information",
    "2. Medical Information",
    "3. AI Ouput Information",
    "4. All Records"
]

# Asked after the filter: look up one patient, or every patient on the date.
QUERY_SCOPE_OPTIONS = [
    "1. One Patient (by Queue Number)",
    "2. All Patients on This Date"
]

REPORT_OPTIONS = [
    "1. Specific Medicine Count",
    "2. Medicine Breakdown",
    "3. Patient Type Breakdown"
]
