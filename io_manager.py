# ======================================================================
# LIBRARY IMPORTS AND CONSTANTS
# ======================================================================

import difflib
import re

import pandas as pd
import phonenumbers

QUIT_SIGNAL = -99
QUIT_COMMAND = "QUIT"
BACK_COMMAND = "BACK"
SYMPTOM_MENU = ["1. Cough",
                "2. Flu",
                "3. Headache",
                "4. Fever",
                "5. Other Symptoms",
                "6. Remove a Symptom",
                "7. Done",
                "You can also input quit or back"]
REG_EXIT_MESSAGE = "Exiting The Registration Process!"
FILE_PATH = "Put here later" #To Be Updated
SYMPTOMS_CSV_PATH = r"datasets/symptoms_umls.csv"

def load_symptoms() -> list:
    """Reads the symptoms dataset. Returns all symptom names in
    uppercase since user input is uppercased before matching."""
    symptoms_dataframe = pd.read_csv(SYMPTOMS_CSV_PATH)
    symptoms_column = symptoms_dataframe["term"].str.upper()
    return symptoms_column.tolist()

SYMPTOMS_DIFFLIB_LIST = load_symptoms()
PRIORITY_KEYLIST = [
    "chest_pain",
    "breathing_difficulties",
    "signs_of_stroke",
    "self_harm",
]

# ======================================================================
# VALIDATION FUNCTIONS
# ======================================================================

# Each validation function takes answer as the input and
# validates it based on a set of predefined conditions.
#
# Each validation function will output either 1) None, which can be
# interpreted as 'No problems', or 2) The error message.
#
# Some questions have a separate validation function since each question
# needs to handle inputs differently.
#
# If multiple questions have identical validation methods they use the
# same function to avoid repetition.
#
# These validation functions are stored in the individual question
# dictionaries in the ALL_QUESTIONS list.
#
# Storing the validation functions in the dictionary establishes a
# logical link between the question and the validation function.
#
# They are accessed dynamically by the run_validation() function, 
# excluding the symptom functions, which are handled separately.

def validate_boolean(user_answer: str) -> str | None:
    """Multiple questions have either Y or N as possible responses,
    so this function is used for all such boolean questions."""
    if user_answer in ["Y", "N"]:
        return None
    else:
        return "Please enter only either 'Y' or 'N'."


def validate_nric(user_answer: str) -> str | None:
    """Regex expression checks that input starts with valid NRIC
    starting letters, followed by 7 digits and a final letter."""
    if bool(re.match(r"^[STMFG]\d{7}[A-Z]$", user_answer)):
        return None
    else:
        return (
            "This is not a valid NRIC format: "
            "ensure it starts with valid nric starting letters, "
            "followed by 7 digits and a final letter. "
        )

def validate_name(user_answer: str) -> str | None:
    """Regex expression checks that input contains only letters for the
    first character, and all other letters are alphabetical, apostrophes
    or hyphens."""
    
    if bool(re.match(r"^[A-Z][A-Z'\- ]*$", user_answer)):
        return None
    else:
        return (
            "This is not a valid name:"
            "only alphabets, spaces, hyphens and apostrophes are allowed."
        )


def validate_gender(user_answer: str) -> str | None:
    if user_answer in ["M", "F"]:
        return None
    else:
        return "This is not a valid input, please only enter either M or F"

def validate_positive_number(user_answer: str) -> str | None:
    # .isdecimal() checks whether the number is a positive integer.
    if user_answer.isdecimal():
        return None
    else:
        return "This is not a valid input, please only enter positive numbers."

def validate_phone_number(user_answer: str) -> str | None:
    """Uses Google's libphonenumber to parse the number and check it
    against real possible numbers.
    Defaults to Singapore if the user leaves out the country code."""

    try:
        # Parses the entered phone number.
        # If there is an error in parsing, the number format was wrong,
        # prompt the user to enter a valid format and try again.
        # Parsing removes spaces, so +6588880000 will also be valid.
        parsed_number = phonenumbers.parse(user_answer, "SG")
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

    
def validate_blank(user_answer: str) -> str | None:
    # Checks if user_answer has a value.
    if user_answer:
        return None
    # If the value is null. returns an error message.
    else:
        return ("Invalid Input ")

def validate_option(option:str):
    is_number = validate_positive_number(option)
    is_blank = validate_blank(option)
    if is_blank:
        error = is_blank
    elif is_number:
        error = is_number
    else:
        error = None
    return error

def symptom_remove(symptom_list:list):
    # Prints the symptom_list
    print(symptom_list, sep=", ")
    # Initialises remove_target to the input value.
    remove_target = (
        input("Please enter the symptom you wish to remove: ").strip().upper()
    )
    if not remove_target:
        print("Input cannot be empty. Please enter a valid input.")
    elif remove_target:
        # Iterates over the list. 
        # If a match is found, it removes the inputted symptom from the list.
        for symptom in symptom_list:
            if remove_target == symptom:
                symptom_list.remove(symptom)
                return

def symptom_diff() -> str:
    # Initialises symptoms to input
    symptom = input("Please enter your symptom here: ").strip().upper()
    # Checks for exact match in valid symptoms list.
    # Returns valid symptom if matched.
    for val_symptom in SYMPTOMS_DIFFLIB_LIST:
        if symptom == val_symptom:
            return val_symptom
    
    # If no exact match exists, 
    # it checks for a list of similar matches using difflib.    
    match_list = difflib.get_close_matches(
        symptom, SYMPTOMS_DIFFLIB_LIST, n=1, cutoff=0.6
    )

    # if matches exist, it grabs the closest one,
    # and prompts the user to check if it is right.
    if match_list:
        closest_match = match_list[0]
        confirmation = (
            input(f"Did you mean '{closest_match}'? (Y/N): ")
            .strip()
            .upper()
        )
        # if user indicates the match is correct, 
        # it returns the matched symptom
        if confirmation == "Y":
            return(closest_match)
    # If there are no matches, 
    # it prints a message for the user to inform them.
    elif not match_list:
        print(
            "This symptom is not in our database, "
            "please enter a valid symptom "
            "or approach a nurse or clerk for assistance!"
        )
    else:
        print(
            "An unprecedented error has occured! "
            "Please approach a nurse, "
            "or administrative clerk for assistance!"
        )
        
def symptom_handler(symptom_list: list) -> list:
    while True:
        header = "Symptoms"
        option = dynamic_menu_print(SYMPTOM_MENU, header)
        # If user inputs quit or back, 
        # reset symptom list and end program.
        symptom = None
        if option == QUIT_COMMAND or option == BACK_COMMAND:
            symptom_list.clear()
            return option
        # For options 1 to 3, 
        # it adds the relevant symptom to the list
        elif option == "1":
            symptom = "COUGH"

        elif option == "2":
            symptom = "FLU"

        elif option == "3":
            symptom = "HEADACHE"
        # For options 4, 
        # it checks if the fever is high or regular, 
        # and sets symptom to it.
        elif option == "4":
            fever_severity = (
                input("Is your fever above 39.0 degrees celcius?(Y/N): ")
                .strip()
                .upper()
            )
            if fever_severity == "Y":
                symptom = "HIGH FEVER"

            elif fever_severity == "N":
                symptom = "FEVER"

            elif not fever_severity:
                print("Input cannot be blank. Please enter Y or N.")

            else:
                print("This is an invalid input. Only type Y or N.")

        elif option == "5":
            # Runs the difflib symptom function.
            symptom=symptom_diff()

        elif option == "6":
            # removes a symptom from the list.
            symptom_remove(symptom_list)

        elif option == "7":
            # Checks if there is at least one symptom in list,
            # if there ism't, prints a error message
            if not symptom_list:
                print(
                    "You have not entered any symptoms, "
                    "please enter at least one symptom!"
                )
            else:
                return symptom_list

        elif not option:
            print("You cannot leave this blank, try again!")

        else:
            print("This is not a valid option number.")

        #If symptom is a valid symptom, it appends it to the list.
        if symptom != None:
            append_list_if_unique(symptom_list, symptom)

def run_validation(ALL_QUESTIONS: dict, user_answer: str, state: int) -> bool:
    """Selects the correct validation function for the current question
    and then runs it to check the user input.

    Returns either True for valid inputs or False for invalid inputs.

    The True / False return values will be used in the run_questions()
    function to determine whether to reprompt or move on to the next
    question."""

    # User input cannot be empty for any question.
    # If it's empty, no validation check is required,
    # immediately return False to signal that input is invalid.
    if not user_answer:
        print("Input cannot be empty. Please enter a valid input.")
        return False

    # Selects the validation function for the current question.
    current_question_validator = ALL_QUESTIONS[state]["validation_function"]

    # Runs the currently selected validation function
    # by passing the current_user_answer into it.
    # Stores the resulting output of either None
    # or the error message string in validation_result.
    validation_result = current_question_validator(user_answer)

    # If validation_result indicates 'No problems', then return True.
    if validation_result == None:
        return True

    # Else validation_result returned an error message string. Print it
    # and return False.
    else:
        print(validation_result)
        return False


# ======================================================================
# SKIP CONDITIONS
# ======================================================================

# Each skip condition takes the answers given so far and returns True
# if the question does not apply to the user.
#
# They are stored in the question dictionaries in the ALL_QUESTIONS list
# under "skip_if", and are accessed by the should_skip() function.

def skip_if_male(answers_dict: dict) -> bool:
    """Males cannot be pregnant, so the pregnancy question is skipped."""
    return answers_dict.get("gender") == "M"


# ======================================================================
# ALL QUESTIONS LIST
# ======================================================================
# List containing dictionaries to store all questions to ask the user.
# Each question and its related details are stored as a dictionary.
# Set share_with_ai to True to explicitly send the information to AI.
# Set skip_if to a skip condition to skip the question when it does not
# apply. Skipped questions are stored as None.

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
        "share_with_ai": True,
    },
    {
        "key": "age",
        "prompt": "Enter your Age: ",
        "validation_function": validate_positive_number,
        "share_with_ai": True,
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
        "skip_if": skip_if_male,
        "share_with_ai": True,
    },
    {
        "key": "chest_pain",
        "prompt": "Are you currently experiencing chest pain? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "breathing_difficulties",
        "prompt": "Are you severely short of breath right now? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "signs_of_stroke",
        "prompt": (
            "Do you have sudden weakness or numbness on one side of your body? (Y/N): "
        ),
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "self_harm",
        "prompt": "Are you having thoughts of harming yourself? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "current_symptoms",
        "prompt": "Please tell us your current symptoms: ",
        "share_with_ai": True,
    },
    {
        "key": "symptom_onset_days",
        "prompt": (
            "How many days ago did your symptoms start? (e.g. 2, or 0 for today): "
        ),
        "validation_function": validate_positive_number,
        "share_with_ai": True,
    },
    {
        "key": "chronic_conditions",
        "prompt": "Are you suffering from any chronic conditions? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "current_medications",
        "prompt": "Are you currently on any medication? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
    {
        "key": "drug_allergies",
        "prompt": "Do you have any drug allergies? (Y/N): ",
        "validation_function": validate_boolean,
        "share_with_ai": True,
    },
]

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def run_questions():
    """Uses a dictionary approach to move between questions.
    all_questions variable stores a list of dictionaries, each one
    containing a question.

    This function cycles through the list of dictionaries to dynamically
    access the correct question based on the current state.

    The output, all_user_responses, will be in structured dictionary
    format."""

    # Initialise state and dictionary to store all answers.
    # Initialise a list for previous symptoms,
    current_state = 0
    all_user_answers = {}
    previous_symptoms=[]
    # Loop until every question has been answered.
    while current_state < len(ALL_QUESTIONS):
        # Returns the current user answer and its validity.
        current_user_answer, answer_is_valid = input_handler(current_state)

        if current_user_answer=="symptoms":
            current_user_answer = symptom_handler(previous_symptoms)
            if type(current_user_answer) == list:
                previous_symptoms = current_user_answer
                answer_is_valid = True

        # Returns QUIT_SIGNAL on quit or the previous state on back.
        # Otherwise the current_state remains unchanged.
        current_state = process_quit_or_back(
            current_user_answer, current_state, all_user_answers
        )
        
        # If the user types quit or consent is "N", exit the function.
        if current_state == QUIT_SIGNAL:
            return

        # If the user typed 'back',
        # skip the rest of the loop and ask the previous question.
        # current_state was already set to QUIT_SIGNAL in process_quit_or_back().
        elif current_user_answer == BACK_COMMAND:
            continue

        # Validates the answer and if valid,
        # stores it and moves to the next question.
        answer_is_valid, current_state = validate_orchestrator(
            answer_is_valid, current_user_answer, current_state, all_user_answers
        )
        # Invalid input, reprompt the same question.
        if answer_is_valid != True:
            continue

    # Adds "ai_bypass":True into the dictionary
    # if any red flag question was answered Y.
    is_priority(all_user_answers)

    return all_user_answers


def back_to_previous_question(state: int, answers_dict: dict) -> int:
    """Sets inputted state to the state of the previous question, which
    brings the user back to the previous question.

    It also removes the previously entered answer from the answers
    dictionary so the user can enter it again.
    """

    if state == 0:
        return state

    previous_state = state - 1

    # Skipped questions were never asked, so they are passed over and
    # the user goes back to the last question they actually answered.
    while previous_state > 0 and should_skip(previous_state, answers_dict):
        answers_dict.pop(ALL_QUESTIONS[previous_state]["key"], None)
        previous_state -= 1

    answers_dict.pop(ALL_QUESTIONS[previous_state]["key"], None)
    return previous_state


def should_skip(state: int, answers_dict: dict) -> bool:
    """Returns True if the question at this state does not apply to the
    user, based on the skip condition stored in its dictionary.
    Questions without a skip condition are always asked."""
    skip_condition = ALL_QUESTIONS[state].get("skip_if")
    if skip_condition is None:
        return False
    return skip_condition(answers_dict)


def process_quit_or_back(user_answer: str, state: int, answers_dict: dict) -> int:
    """
    This function handles when the user presses quit or back.
    """
    if user_answer == QUIT_COMMAND or (
        ALL_QUESTIONS[state]["key"] == "consent" and user_answer == "N"
    ):
        state = QUIT_SIGNAL
        print(REG_EXIT_MESSAGE)
        return state
    elif user_answer == BACK_COMMAND:
        if state > 0:
            state = back_to_previous_question(state, answers_dict)
            return state

        else:
            print(
                "There is no further step to go back to. "
                "If you would like to exit, type 'quit'."
            )
    return state

def append_list_if_unique(list: list, user_answer: str):
    for value in list:
        if value == user_answer:
            print("This value already exists in the list!")
            return list
    list.append(user_answer)

def answers_appending(user_answer: str, answers_dict: dict, state: int) -> int:
    # Stores the answer and moves on to the next question.
    answers_dict[ALL_QUESTIONS[state]["key"]] = user_answer
    state += 1

    # Any following questions that do not apply to the user are stored
    # as None and skipped.
    while state < len(ALL_QUESTIONS) and should_skip(state, answers_dict):
        answers_dict[ALL_QUESTIONS[state]["key"]] = None
        state += 1
    return state

def is_priority(answers_dict: dict) -> dict:
    """
    Creates or sets the value of the dictionary key to True or False as it is a bool, 
    based off whether the user replied Y to any of the concerning questions.
    """
    answers_dict["priority"] = False

    for questions, value in answers_dict.items():
        if questions in PRIORITY_KEYLIST and value == "Y":
            answers_dict["priority"] = True

    # For edge cases like an underage girl being pregnant
    if answers_dict.get("pregnancy") == "Y" and int(answers_dict["age"]) < 16:
        answers_dict["priority"] = True

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
    # If current question is symptoms, 
    # it returns symptoms as it has separate handling logic.
    if ALL_QUESTIONS[state]["key"] == "current_symptoms":
        current_user_answer="symptoms"

    # For any other key value it prints the prompt of the key,
    # and sets the user's input as current_user_answer.
    else:
        current_question = ALL_QUESTIONS[state]
        current_user_answer = input(f"{current_question['prompt']}").upper().strip()
    # returns current_user_answer at the end of function
    return current_user_answer, None

def build_confirmation_menu(answers_dict: dict) -> tuple:
    """Builds one menu line per question in ALL_QUESTIONS, so each menu
    number always matches the question's state plus one, regardless of
    the order of the keys in answers_dict.

    Returns the menu options, with Confirm All Inputs as the last
    option, and the list of states the user is allowed to edit."""
    confirmation_menu_options = []
    editable_states = []

    for state, question in enumerate(ALL_QUESTIONS):
        # Skipped questions do not apply to the user,
        # so the value is shown as Not Applicable
        # and the question cannot be edited.
        if should_skip(state, answers_dict):
            value = "Not Applicable"
        else:
            value = answers_dict.get(question["key"])
            editable_states.append(state)
        confirmation_menu_options.append(
            f"{state + 1:02d}. {question['prompt']}{value}"
        )

    # Appends the option to confirm all inputs to the list of options.
    confirmation_option = len(ALL_QUESTIONS) + 1
    confirmation_menu_options.append(f"{confirmation_option:02d}. Confirm All Inputs")
    return confirmation_menu_options, editable_states

def finalise_answers(answers_dict: dict) -> bool:
    """Prepares the answers to be confirmed.

    Skipped questions do not apply, so their answers are set to None.
    A question that was skipped before may now apply (e.g. gender
    changed from M to F), so it must be answered before confirming.

    Returns True if every question that applies has been answered,
    otherwise prints which question is missing and returns False."""
    for state, question in enumerate(ALL_QUESTIONS):
        if should_skip(state, answers_dict):
            answers_dict[question["key"]] = None
        elif answers_dict.get(question["key"]) is None:
            print(
                f"You have not answered '{question['prompt'].strip()}' "
                "Please answer it before confirming your inputs."
            )
            return False

    # Updates the dictionary of answers with the latest priority status.
    is_priority(answers_dict)
    return True

def edit_answer(state: int, answers_dict: dict) -> bool:
    """Asks the question at this state again, and stores the new answer
    if it is valid.

    Returns True if the user typed quit, otherwise False."""
    revised_answer, answer_is_valid = input_handler(state)

    # If the current question is symptoms, it automatically returns symptoms.
    # Therefore to check for symptoms we check if revised answer is symptoms.
    if revised_answer == "symptoms":
        # Runs a copy of the previous symptoms through the symptom handler,
        # as lists are mutable objects. That way, the previous symptoms
        # are kept unchanged if the user types back or quit.
        previous_symptoms = answers_dict.get("current_symptoms")
        revised_answer = symptom_handler(previous_symptoms.copy())
        # Sets answer_is_valid to True, as symptom_handler has built in validation.
        answer_is_valid = True

    # If user inputs back,
    # it will warn the user that backing out of confirmation isnt possible.
    if revised_answer == BACK_COMMAND:
        print("You cannot go back during the confirmation process. "
              "Please enter a valid input.")
        return False

    if revised_answer == QUIT_COMMAND:
        return True

    # Runs the user input through the validate orcherstrator function,
    # which will run the appropriate validation function to check inputs,
    # and stores the answer if it is valid.
    validate_orchestrator(answer_is_valid, revised_answer, state, answers_dict)
    return False

def confirm_inputs(answers_dict: dict) -> bool | None:
    """Shows every answer so the user can edit any of them before
    confirming.

    Returns True once the answers are confirmed, or None if the user
    types quit or changes consent to N."""
    header = "Confirmation Screen"
    # Confirmation should break if user chooses to change consent to N
    while answers_dict["consent"] == "Y":
        confirmation_menu_options, editable_states = (
            build_confirmation_menu(answers_dict)
        )
        # Prints the menu and gets input as menu_state.
        menu_state = dynamic_menu_print(confirmation_menu_options, header)

        # Runs the function to check if menu_state is a valid input.
        error=validate_option(menu_state)
        # If the function returns a error, 
        # print the error and loop back to the start.
        if error:
            print(error)
            continue
        # Confirm All Inputs is the last option in the menu.
        if int(menu_state) == len(confirmation_menu_options):
            if finalise_answers(answers_dict):
                return True
            continue

        # Menu numbers are the question states with one added to them,
        # so one has to be deducted in order to edit the right question.
        state_to_edit = int(menu_state) - 1

        # Check if the question is within the valid range,
        # and prints a error message if it isnt.
        if not 0 <= state_to_edit < len(ALL_QUESTIONS):
            print("Invalid input. Please enter a valid menu option!")
            continue

        # Check if the question can be edited.
        # If it is not, print a error message and loop back to the start.
        if state_to_edit not in editable_states:
            print("That item cannot be edited.")
            continue

        # If the user types quit while editing, exit confirmation.
        if edit_answer(state_to_edit, answers_dict):
            break

    # Only way to break out of the while loop,
    # is if user changes consent to N or if user types quit
    return None

def dynamic_menu_width(menu_list: list) -> int:
    """
    Looks for the longest string in a list,
    and returns its value +4 as the output.
    The +4 is due to needing to account for space for the | and " ".
    """
    if menu_list:
     menu_width=len(max(menu_list, key=len))+4
     return menu_width

def dynamic_menu_print(menu_options: list, menu_header: str | None = None) -> str:
    """
    Prints the menu, based off the menu list,
    with the dynamic width separator.
    Ensures the menu print is properly formatted and centered.
    The header is optional; if omitted, only the options are printed.
    """
    menu_width = dynamic_menu_width(menu_options)
    menu_separator = menu_width * "-"
    print(menu_separator)

    if menu_header:
        print("|" + menu_header.center(menu_width - 2) + "|")
        print(menu_separator)

    for option in menu_options:
        print("|" + f" {option}".ljust(menu_width - 2) + "|")
    print(menu_separator)

    option = input("Please enter one of the above options: ").strip().upper()
    return option


def filter_answers(answers_dict: dict) -> dict:
    """Returns a new dictionary with only the answers whose question is
    marked share_with_ai, so personal information is never sent to AI.
    """
    answers_filtered = {}
    for question in ALL_QUESTIONS:
        if question.get("share_with_ai", False):
            key = question["key"]
            answers_filtered[key] = answers_dict.get(key)
    return answers_filtered



def print_text(text: str) -> None:
    """Prints a message to the patient, such as the AI error message."""
    print(text)
