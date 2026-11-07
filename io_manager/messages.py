"""
All of the strings in this file are constants that are used by the IO manager
to display prompts, errors, and messages to the patient. 
This means that every module in the package can use these strings without having to import anything else.
"""

# ======================================================================
# SHARED PROMPTS AND ERRORS
# ======================================================================
MENU_OPTION_PROMPT = "Please enter one of the above options: "
EMPTY_INPUT_ERROR = "Input cannot be empty. Please enter a valid input."
NOT_APPLICABLE = "Not Applicable"
NOT_ANSWERED = "Not Answered"

# ======================================================================
# REGISTRATION FLOW
# ======================================================================
REG_EXIT_MESSAGE = "Exiting The Registration Process!"
NO_PREVIOUS_QUESTION = (
    "There is no further step to go back to. "
    "If you would like to exit, type 'quit'."
)
NURSE_ALERT_MESSAGE = (
    "You need immediate medical attention. "
    "Please approach a nurse right away for help."
)
MANUAL_REGISTRATION_MESSAGE = "Please proceed to manual registration."
CONFIRMED_MESSAGE = "Thank you for confirming your inputs."

# ======================================================================
# QUESTION PROMPTS
# ======================================================================
CONSENT_PROMPT = (
    "Do you consent to sharing your data? "
    "Consent is required to continue with the registration process. (Y/N): "
)
NAME_PROMPT = "Enter your Name: "
NRIC_PROMPT = "Enter your NRIC: "
GENDER_PROMPT = "Enter your Gender [M/F]: "
AGE_PROMPT = "Enter your Age: "
PHONE_PROMPT = (
    "Please enter your country code and phone number "
    "in the following format (+65 88880000): "
)
PREGNANCY_PROMPT = "Are you currently pregnant? (Y/N): "
CHEST_PAIN_PROMPT = "Are you currently experiencing chest pain? (Y/N): "
BREATHING_PROMPT = "Are you severely short of breath right now? (Y/N): "
STROKE_PROMPT = (
    "Do you have sudden weakness or numbness on one side of your body? (Y/N): "
)
SELF_HARM_PROMPT = "Are you having thoughts of harming yourself? (Y/N): "
SYMPTOMS_PROMPT = "Please tell us your current symptoms: "
ONSET_PROMPT = (
    "How many days ago did your symptoms start? (e.g. 2, or 0 for today): "
)
CHRONIC_PROMPT = "Are you suffering from any chronic conditions? (Y/N): "
MEDICATIONS_PROMPT = "Are you currently on any medication? (Y/N): "
ALLERGIES_PROMPT = "Do you have any drug allergies? (Y/N): "

# ======================================================================
# VALIDATION ERRORS
# ======================================================================
YES_NO_ERROR = "Please enter only either 'Y' or 'N'."
NRIC_ERROR = (
    "This is not a valid NRIC format: ensure it starts with a valid NRIC "
    "starting letter, followed by 7 digits and a final letter."
)
NAME_ERROR = (
    "This is not a valid name: "
    "only alphabets, spaces, hyphens and apostrophes are allowed."
)
GENDER_ERROR = "This is not a valid input, please only enter either M or F."
POSITIVE_WHOLE_NUMBER_ERROR = (
    "This is not a valid input, please only enter positive whole numbers."
)
# {maximum} is filled in by RegistrationFactory with the upper bound used.
AGE_ERROR = "This is not a valid age, please enter a whole number from 0 to {maximum}."
ONSET_DAYS_ERROR = (
    "This is not a valid number of days, "
    "please enter a whole number from 0 to {maximum}."
)
PHONE_FORMAT_ERROR = (
    "This is not a valid phone number format: "
    "please enter your country code then your number (e.g. +65 88880000)."
)
PHONE_INVALID_ERROR = (
    "This phone number is not valid for its country: "
    "please check the number and country code."
)
DATE_ERROR = "Please enter a valid date in YYYY-MM-DD format (e.g. 2026-10-13)."

# ======================================================================
# SYMPTOM MENU
# ======================================================================
SYMPTOM_MENU_HEADER = "Symptoms"
SYMPTOM_MENU_HINT = "You can also input quit or back"
COUGH_LABEL = "Cough"
FLU_LABEL = "Flu"
HEADACHE_LABEL = "Headache"
FEVER_LABEL = "Fever"
OTHER_SYMPTOMS_LABEL = "Other Symptoms"
REMOVE_SYMPTOM_LABEL = "Remove a Symptom"
DONE_LABEL = "Done"
SYMPTOM_MENU_BLANK_ERROR = "You cannot leave this blank, try again!"
SYMPTOM_MENU_OPTION_ERROR = "This is not a valid option number."
NO_SYMPTOMS_ERROR = (
    "You have not entered any symptoms, please enter at least one symptom!"
)
DUPLICATE_SYMPTOM_ERROR = "This value already exists in the list!"
FEVER_PROMPT = "Is your temperature 39.0 °C or higher? (Y/N): "
SYMPTOM_ENTRY_PROMPT = "Please enter your symptom here: "
SYMPTOM_NOT_FOUND = (
    "This symptom is not in our database, please enter a valid symptom "
    "or approach a nurse or clerk for assistance!"
)
SYMPTOM_CONFIRM_PROMPT = "Did you mean '{symptom}'? (Y/N): "
CURRENT_SYMPTOMS = "Your symptoms: {symptoms}"
NO_SYMPTOMS_TO_REMOVE = "You have not entered any symptoms to remove."
REMOVE_SYMPTOM_PROMPT = (
    "Please enter the symptom you wish to remove, "
    "or {remove_all} to remove every symptom: "
)
ALL_SYMPTOMS_REMOVED = "All your symptoms have been removed."
SYMPTOM_NOT_IN_LIST = "'{symptom}' is not in your list."

# ======================================================================
# CONFIRMATION SCREEN
# ======================================================================
CONFIRMATION_HEADER = "Confirmation Screen"
CONFIRM_ALL_LABEL = "Confirm All Inputs"
CONFIRMATION_MENU_HINT = "You can also input quit"
INVALID_MENU_OPTION = "Invalid input. Please enter a valid menu option!"
CANNOT_EDIT = "That item cannot be edited."
CANNOT_GO_BACK = (
    "You cannot go back during the confirmation process. "
    "Please enter a valid input."
)
UNANSWERED_QUESTION = (
    "You have not answered '{prompt}'. "
    "Please answer it before confirming your inputs."
)

# ======================================================================
# RESULT SCREEN
# ======================================================================
RESULT_HEADER = "Registration Complete"
QUEUE_NUMBER_LINE = "Your Queue Number: {queue_number}"
DIAGNOSIS_TITLE_LINE = "{diagnosis} Diagnosis: {title}"
MEDICINES_HEADING = "  Medicines:"
MEDICINE_LINE = "    - {medicine}"
# What the patient should do next for each route from logic_manager.
ROUTE_MESSAGES = {
    "EMERGENCY": (
        "This may be an EMERGENCY. "
        "Please approach a staff member right away and show them this "
        "queue number."
    ),
    "Doctor": (
        "Please take a seat and wait for your queue number to be called "
        "to see a doctor."
    ),
    "Pharmacist": (
        "Please proceed to the pharmacy and wait for your queue number "
        "to be called."
    ),
    "Retail": (
        "You do not need to see a doctor or pharmacist. "
        "The medicines below can be bought from any retail store."
    ),
}
RETAIL_DISCLAIMER = (
    "This is not a final diagnosis. If your symptoms get worse or do not "
    "improve, please see a doctor."
)
