# ======================================================================
# LIBRARY IMPORTS AND CONSTANTS
# ======================================================================

import re

QUIT_SIGNAL = -99
QUIT_COMMAND = "QUIT"
BACK_COMMAND = "BACK"
FILE_PATH = "Put here later" #To Be Updated


def validate_boolean(current_user_answer: str) -> str | None:
    """Multiple questions have either Y or N as possible responses,
    so this function is used for all such boolean questions."""
    if current_user_answer in ["Y", "N"]:
        return None
    else:
        return "Please enter only either 'Y' or 'N'."


def validate_nric(current_user_answer: str) -> str | None:
    """Regex expression checks that input starts with valid NRIC
    starting letters, followed by 7 digits and a final letter."""
    if bool(re.match(r"^[STMFG]\d{7}[A-Z]$", current_user_answer)):
        return None
    else:
        return (
            "This is not a valid NRIC format: "
            "ensure it starts with valid nric starting letters, "
            "followed by 7 digits and a final letter. "
        )

def validate_name(current_user_answer: str) -> str | None:
    """Regex expression checks that input contains only letters for the
    first character, and all other letters are alphabetical, apostrophes
    or hyphens."""
    
    if bool(re.match(r"^[A-Z][A-Z'\- ]*$", current_user_answer)):
        return None
    else:
        return (
            "This is not a valid name:"
            "only alphabets, spaces, hyphens and apostrophes are allowed."
        )


def validate_gender(current_user_answer: str) -> str | None:
    if current_user_answer in ["M", "F"]:
        return None
    else:
        return "This is not a valid input, please only enter either M or F"


def validate_age(input : str) -> str | None:
    """Validate age based on whether it is a positive integer using is.digit()"""
    if input.isdigit():
        validated_flag = True
    else:
        validated_flag = False
        print("This is not a valid input, please only enter positive numbers for age")
    return validated_flag


def run_validation(questions: dict, current_user_answer: str, current_state: int) -> bool:
    """Selects the correct validation function for the current question and runs it.
    Returns either True for valid inputs or False for invalid inputs.
    The True / False return values will be used in the run_questions() function to determine whether to reprompt or move onto next question."""

    # User input cannot be empty for any question. 
    # If it's empty the validation function isnt needed, immediately return False for invalid input.
    if not current_user_answer:
        print("Input cannot be empty. Please enter a valid input.")
        return False


    # selects the validation function for the current question
    current_question_validator = questions[current_state]["validation_function"]

    # runs the currently selected validation function by passing the current_user_answer into it
    # stores the resulting output of either none or the error message string in validation_result
    validation_result = current_question_validator(current_user_answer)

    # if validation_result indicates 'None problems' then return True 
    if validation_result is None:
        return True

    # else validation_result returned a error message string. Print it and return False
    else:
        print(validation_result)
        return False


# =============================================================================
# ALL QUESTIONS LIST
# =============================================================================
# List containing dictionaries to store all questions to ask the user, used by run_questions()
# Each question and its related details is stored as a dictionary
ALL_QUESTIONS = [
    {
        "key": "consent",
        "prompt": "Do you consent to sharing your data? Consent is required to continue with the registration process. (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "name",
        "prompt": "Enter your Name: ",
        "validation_function": validate_name
    },
    {
        "key": "nric",
        "prompt": "Enter your NRIC: ",
        "validation_function": validate_nric
    },
    {
        "key": "gender",
        "prompt": "Enter your Gender [M/F]: ",
        "validation_function": validate_gender
    },
    {
        "key": "age",
        "prompt": "Enter your Age: ",
        "validation_function": ""
    },
    {
        "key": "phone_number",
        "prompt": "Please enter your country code and phone number in the following format (+65 88880000): ",
        "validation_function": ""
    },
    {
        "key": "pregnancy",
        "prompt": "Are you currently pregnant? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "red_flag_chest_pain",
        "prompt": "Are you currently experiencing chest pain? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "red_flag_breathing",
        "prompt": "Are you severely short of breath right now? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "red_flag_stroke",
        "prompt": "Do you have sudden weakness or numbness on one side of your body? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "self_harm",
        "prompt": "Are you having thoughts of harming yourself? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "current_symptoms",
        "prompt": "Please tell us your current symptoms: ",
        "validation_function": ""
    },
    {
        "key": "symptom_onset",
        "prompt": "When did your symptoms start? (e.g. 2 days ago): ",
        "validation_function": ""
    },
    {
        "key": "chronic_conditions",
        "prompt": "Are you suffering from any chronic conditions? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "current_medications",
        "prompt": "Are you currently on any medication? (Y/N): ",
        "validation_function": validate_boolean
    },
    {
        "key": "drug_allergies",
        "prompt": "Do you have any drug allergies? (Y/N): ",
        "validation_function": validate_boolean
    }
]


def run_questions():
    """Use dictionary approach to move between questions.
    all_questions variable stores a list of dictionaries, each dict containing a question.
    This function cycles through the list of dictionaries to dynamically access the correct 
    question based on the current state.
    
    The output, all_user_responses will be in structured dictionary format."""

    # initialise state and answers dict to store all responses
    state = 0
    all_user_responses = {}

    while state < len(ALL_QUESTIONS):

        # this tells which dictionary to point at
        # intiially, all_questions[0] since state = 0, which refers to the consent dictionary
        question_index = ALL_QUESTIONS[state]
        
        # ask the "prompt" value of the currently selected dictionary
        response = input(f"{question_index["prompt"]}")

        # stores the answer in the answers dictionary with the corresponding "key"
        all_user_responses[question_index["key"]] = response

        # increments state by 1 to move onto the next question, till all questions completed
        state += 1
    #Checks if the program has finished running successfully
    #Only scenario where the length of responses and questions wont be equal is if user quits program or refuses consent
    if len(all_user_responses) == len(ALL_QUESTIONS):
        # return the final dictionary with all answers to the questions
        return all_user_responses
    else:
        #User has quit or refused consent
        print("You have either refused consent or quit.")
        print("Exiting back to Menu! Have a nice day.")

