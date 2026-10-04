# =============================================================================
# LIBRARY IMPORTS AND CONSTANTS
# =============================================================================

import re
import phonenumbers
import difflib

QUIT_SIGNAL = -99
QUIT_COMMAND = "QUIT"
BACK_COMMAND = "BACK"
FILE_PATH = "Put here later" #To Be Updated

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

def validate_boolean(current_user_answer: str) -> str | None:
    """
    Multiple questions have either Y or N as possible responses, 
    so this function is used for all of such boolean questions
    """
    if current_user_answer in ["Y", "N"]:
        return None
    else:
        return "Please enter only either 'Y' or 'N'."

def validate_nric(input : str):
    # Assigns validated_flag bool value using a regex match expression from the re library
    # Regular expression checks that input starts with valid nric starting letters, followed by 7 digits and a final letter
    validated_flag = bool(re.match(r"^[STMFG]\d{7}[A-Z]$", input))

    return validated_flag

def validate_name(input : str):
    """validate name based on regex expression"""
    # Conditional checks regex and expression
    # Regex expression checks that input contains only letters for the first character, and all other letters are alphabetical, apostrophes or hyohens
    if bool(re.match(r"^[A-Z][A-Z'-]*$", input)):
        validated_flag =  True
    else:
        validated_flag = False
        print("This is not a valid name, only alphabets, spaces, hyphens and apostrophes are allowed!")

    return validated_flag

def validate_gender(input : str) -> str | None:
    if input == "M" or input == "F":
        validated_flag = True
    else:
        validated_flag = False
        print("This is not a valid input, please only enter either M or F")
    return validated_flag


def validate_age(input : str) -> str | None:
    """Validate age based on whether it is a positive integer using is.digit()"""
    if input.isdigit():
        validated_flag = True
    else:
        validated_flag = False
        print("This is not a valid input, please only enter positive numbers for age")
    return validated_flag

def validate_orchestator(input : str,state : int):
    while True:
        if input == "QUIT" or input == "BACK" :
            validated_flag = True
            break
        if not input :
            validated_flag = False
            print("Your input cannot be blank, please try again!")
            break
        if state == 0:
            validated_flag, state = validate_consent(input, state)
            break
        if state == 1:
            validated_flag = validate_name(input)
            break
        if state == 2:
            validated_flag = validate_nric(input)
            break
        if state == 3:
            validated_flag = validate_gender(input)
        else:
            validated_flag = True
            break
    return validated_flag, state

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


all_user_responses=run_questions()

