# ======================================================================
# LIBRARY IMPORTS AND CONSTANTS
# ======================================================================

import re

import phonenumbers

QUIT_SIGNAL = -99
QUIT_COMMAND = "QUIT"
BACK_COMMAND = "BACK"
FILE_PATH = "Put here later" #To Be Updated

PRIORITY_KEYLIST = [
    "chest_pain",
    "breathing_difficulties",
    "signs_of_stroke",
    "self_harm",
]


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

def validate_positive_number(current_user_answer: str) -> str | None:
    # .isdigit() checks whether the number is a positive integer.
    if current_user_answer.isdigit():
        return None
    else:
        return "This is not a valid input, please only enter positive numbers."

def validate_phone_number(current_user_answer: str) -> str | None:
    """Uses Google's libphonenumber to parse the number and check it
    against real possible numbers.
    Defaults to Singapore if the user leaves out the country code."""

    try:
        # Parses the entered phone number.
        # If there is an error in parsing, the number format was wrong,
        # prompt the user to enter a valid format and try again.
        # Parsing removes spaces, so +6588880000 will also be valid.
        parsed_number = phonenumbers.parse(current_user_answer, "SG")
    except phonenumbers.NumberParseException:
        return (
            "This is not a valid phone number format: "
            "please enter your country code then your number (e.g. +65 88880000)."
        )

    # If the number is valid then return None.
    # If not, return an error message.
    if phonenumbers.is_valid_number(parsed_number):
        return None
    else:
        return (
            "This phone number is not valid for its country: "
            "please check the number and country code."
        )


def run_validation(ALL_QUESTIONS: dict, current_user_answer: str, current_state: int) -> bool:
    """Selects the correct validation function for the current question
    and then runs it to check the user input.

    Returns either True for valid inputs or False for invalid inputs.

    The True / False return values will be used in the run_questions()
    function to determine whether to reprompt or move on to the next
    question."""

    # User input cannot be empty for any question.
    # If it's empty, no validation check is required,
    # immediately return False to signal that input is invalid.
    if not current_user_answer:
        print("Input cannot be empty. Please enter a valid input.")
        return False

    # Selects the validation function for the current question.
    current_question_validator = ALL_QUESTIONS[current_state]["validation_function"]

    # Runs the currently selected validation function
    # by passing the current_user_answer into it.
    # Stores the resulting output of either None
    # or the error message string in validation_result.
    validation_result = current_question_validator(current_user_answer)

    # If validation_result indicates 'No problems', then return True.
    if validation_result == None:
        return True

    # Else validation_result returned an error message string. Print it
    # and return False.
    else:
        print(validation_result)
        return False


# ======================================================================
# ALL QUESTIONS LIST
# ======================================================================
# List containing dictionaries to store all questions to ask the user.
# Each question and its related details are stored as a dictionary.

ALL_QUESTIONS = [
    {
        "key": "consent",
        "prompt": (
            "Do you consent to sharing your data? "
            "Consent is required to continue with the registration process. (Y/N): "
        ),
        "validation_function": validate_boolean,
    },
    {
        "key": "name",
        "prompt": "Enter your Name: ",
        "validation_function": validate_name,
    },
    {
        "key": "nric",
        "prompt": "Enter your NRIC: ",
        "validation_function": validate_nric,
    },
    {
        "key": "gender",
        "prompt": "Enter your Gender [M/F]: ",
        "validation_function": validate_gender,
    },
    {
        "key": "age",
        "prompt": "Enter your Age: ",
        "validation_function": validate_positive_number,
    },
    {
        "key": "phone_number",
        "prompt": (
            "Please enter your country code and phone number "
            "in the following format (+65 88880000): "
        ),
        "validation_function": validate_phone_number,
    },
    {
        "key": "pregnancy",
        "prompt": "Are you currently pregnant? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "chest_pain",
        "prompt": "Are you currently experiencing chest pain? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "breathing_difficulties",
        "prompt": "Are you severely short of breath right now? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "signs_of_stroke",
        "prompt": (
            "Do you have sudden weakness or numbness on one side of your body? (Y/N): "
        ),
        "validation_function": validate_boolean,
    },
    {
        "key": "self_harm",
        "prompt": "Are you having thoughts of harming yourself? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "current_symptoms",
        "prompt": "Please tell us your current symptoms: ",
    },
    {
        "key": "symptom_onset",
        "prompt": (
            "How many days ago did your symptoms start? (e.g. 2, or 0 for today): "
        ),
        "validation_function": validate_positive_number,
    },
    {
        "key": "chronic_conditions",
        "prompt": "Are you suffering from any chronic conditions? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "current_medications",
        "prompt": "Are you currently on any medication? (Y/N): ",
        "validation_function": validate_boolean,
    },
    {
        "key": "drug_allergies",
        "prompt": "Do you have any drug allergies? (Y/N): ",
        "validation_function": validate_boolean,
    },
]

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

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


def back_to_previous_question(current_state: int, answers: dict) -> int:
    """Sets current_state to the state of the previous question, which
    brings the user back to the previous question.

    It also removes the previously entered answer from the answers
    dictionary so the user can enter it again.
    """

    if current_state == 0:
        return current_state

    current_question_key = ALL_QUESTIONS[current_state]["key"]
    previous_state = current_state - 1
    previous_question = ALL_QUESTIONS[previous_state]
    previous_question_key = previous_question["key"]
    answers.pop(previous_question_key, None)

    if current_question_key == "chest_pain" and answers["gender"] == "M":
        previous_state = previous_state - 1
        previous_question = ALL_QUESTIONS[previous_state]
        previous_question_key = previous_question["key"]
        answers.pop(previous_question_key, None)

    return previous_state


def quit_or_back_handler(input: str, state: int, answers_dict: dict) -> int:
    """
    This function handles when the user presses quit or back.
    """
    if input == QUIT_COMMAND or (
        ALL_QUESTIONS[state]["key"] == "consent" and input == "N"
    ):
        state = QUIT_SIGNAL
        print(
            "You have chosen to exit the registration process. Thank you for your time."
        )
        return state
    elif input == BACK_COMMAND:
        if state > 0:
            state = back_to_previous_question(state, answers_dict)
            return state

        else:
            print(
                "There is no further step to go back to. "
                "If you would like to exit, type 'quit'."
            )
    return state

def list_dedupe_append(list: list, input: str):
    for value in list:
        if value == input:
            print("This value already exists in the list!")
            return list
    list.append(input)

def answers_appending(answer: str, answers_dict: dict, state: int) -> dict | int:
    # Checks if the next question is the pregnancy question and if the
    # user is male.
    if state == 5 and answers_dict["gender"] == "M":
        # Appends the answer to the current question and skips the
        # pregnancy question if the user is male.
        answers_dict[ALL_QUESTIONS[state]["key"]] = answer
        # Adds 1 to the state to effectively skip the pregnancy question
        # and move to the next question.
        state += 1
        # Appends None to the answers_dict for the pregnancy question.
        answers_dict[ALL_QUESTIONS[state]["key"]] = None
    else:
        answers_dict[ALL_QUESTIONS[state]["key"]] = answer
    state += 1
    return state

def is_priority(answers_dict: dict) -> dict:
    answers_dict["priority"] = False
    for questions, value in answers_dict.items():
        if questions in PRIORITY_KEYLIST and value == "Y":
            answers_dict["priority"] = True
            break

def validate_orchestrator(
    isvalid_answer: bool, user_answer: str, state: int, answers_dict: dict
) -> bool:
    if isvalid_answer is None:
        # Runs the validation function on the current question which
        # returns True for valid and False for invalid user input.
        isvalid_answer = run_validation(ALL_QUESTIONS, user_answer, state)

    # If the input is valid.
    if isvalid_answer == True:
        # Stores the valid response and moves on to the next step.
        state = answers_appending(user_answer, answers_dict, state)

    return isvalid_answer, state

def input_handler(state: int) -> list | bool | int:
    if ALL_QUESTIONS[state]["key"] == "current_symptoms":
        current_user_answer="symptoms"
    else:
        current_question = ALL_QUESTIONS[state]
        current_user_answer = input(f"{current_question['prompt']}").upper().strip()

    return current_user_answer, None
