# ======================================================================
# LIBRARY IMPORTS AND CONSTANTS
# ======================================================================

import difflib
import re
import textwrap
from datetime import datetime

import pandas as pd
import phonenumbers

import data_manager as data

QUIT_SIGNAL = -99
QUIT_COMMAND = "QUIT"
BACK_COMMAND = "BACK"
REG_EXIT_MESSAGE = "Exiting The Registration Process!"

def load_symptoms() -> list:
    """Reads the symptoms dataset. Returns all symptom names in
    uppercase since user input is uppercased before matching."""
    symptoms_dataframe = pd.read_csv(data.SYMPTOMS_CSV_PATH)
    symptoms_column = symptoms_dataframe["term"].str.upper()
    return symptoms_column.tolist()

SYMPTOMS_DIFFLIB_LIST = load_symptoms()
# Answering Y to any of these questions means the user needs a nurse
# immediately, so registration stops straight away.
EMERGENCY_KEYS = [
    "chest_pain",
    "breathing_difficulties",
    "signs_of_stroke",
    "self_harm",
]
NURSE_ALERT_MESSAGE = (
    "You need immediate medical attention. "
    "Please approach a nurse right away for help."
)
# Users under this age cannot self register, so registration stops.
MINIMUM_AGE = 18
MANUAL_REGISTRATION_MESSAGE = "Please proceed to manual registration."

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
# They are accessed dynamically by the run_validation() function.
# Questions with an input_function (e.g. symptoms) validate their own
# input and do not need a validation function.

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

def validate_decimal_integer(user_answer: str) -> str | None:
    # Validates whole numbers for 0 and higher.
    # .isdecimal() only accepts the digits 0-9, so negative signs
    # and decimal points are rejected.
    # Used for symptom onset days, where 0 means today.
    if user_answer.isdecimal():
        return None
    else:
        return "This is not a valid input, please only enter whole numbers."

def validate_positive_integer(user_answer: str) -> str | None:
    # Validates whole numbers for 1 and above, so 0 is rejected.
    # .isdecimal() is checked first so int() never receives invalid input.
    # Used for age and menu options, which start from 1.
    if user_answer.isdecimal() and int(user_answer) > 0:
        return None
    else:
        return "This is not a valid input, please only enter positive whole numbers."

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

    
def validate_empty(user_answer: str) -> str | None:
    # Checks if user_answer has a value.
    if user_answer:
        return None
    # If the value is null. returns an error message.
    else:
        return ("Invalid Input ")

def validate_option(option:str):
    is_number = validate_positive_integer(option)
    is_blank = validate_empty(option)
    if is_blank:
        error = is_blank
    elif is_number:
        error = is_number
    else:
        error = None
    return error

def validate_date(user_answer: str):
    error = "Please enter a valid date in YYYY-MM-DD format (e.g. 2026-10-13)."
    user_answer = user_answer.strip()

    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", user_answer):
        return error

    try:
        datetime.strptime(user_answer, "%Y-%m-%d")
    except ValueError:
        return error

    return None

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

def match_symptom(symptom: str) -> tuple:
    """Looks up the symptom in the symptoms dataset.

    Returns (symptom, True) for an exact match, (closest symptom, False)
    for a close match found by difflib, or (None, False) if there is no
    match."""
    if symptom in SYMPTOMS_DIFFLIB_LIST:
        return symptom, True

    # If no exact match exists,
    # it checks for the closest similar match using difflib.
    match_list = difflib.get_close_matches(
        symptom, SYMPTOMS_DIFFLIB_LIST, n=1, cutoff=0.6
    )
    if match_list:
        return match_list[0], False
    return None, False

def symptom_diff() -> str | None:
    """Asks for a symptom and matches it to the symptoms dataset.

    Returns the matched symptom, or None if there is no match or the
    user rejects the closest match."""
    symptom = input("Please enter your symptom here: ").strip().upper()
    matched_symptom, is_exact_match = match_symptom(symptom)

    if matched_symptom is None:
        print(
            "This symptom is not in our database, "
            "please enter a valid symptom "
            "or approach a nurse or clerk for assistance!"
        )
        return None

    if is_exact_match:
        return matched_symptom

    # For a close match, the user is asked to check if it is right.
    confirmation = (
        input(f"Did you mean '{matched_symptom}'? (Y/N): ").strip().upper()
    )
    if confirmation == "Y":
        return matched_symptom
    return None

def fever_severity() -> str | None:
    """Asks whether the fever is high or regular.

    Returns HIGH FEVER or FEVER, or None if the input is invalid."""
    fever_answer = (
        input("Is your fever above 39.0 degrees celcius? (Y/N): ").strip().upper()
    )
    validation_result = validate_boolean(fever_answer)
    if validation_result is not None:
        print(validation_result)
        return None

    if fever_answer == "Y":
        return "HIGH FEVER"
    return "FEVER"

# List containing dictionaries to store the symptom menu options.
# The position in the list sets the menu number, starting from 1.
# Set symptom to add that symptom directly when the option is chosen.
# Set ask_function to ask a follow up question instead. It returns the
# symptom to add, or None if no symptom should be added.
# Remove a Symptom and Done are always added after these options.

SYMPTOM_OPTIONS = [
    {"label": "Cough", "symptom": "COUGH"},
    {"label": "Flu", "symptom": "FLU"},
    {"label": "Headache", "symptom": "HEADACHE"},
    {"label": "Fever", "ask_function": fever_severity},
    {"label": "Other Symptoms", "ask_function": symptom_diff},
]
REMOVE_SYMPTOM_OPTION = str(len(SYMPTOM_OPTIONS) + 1)
DONE_OPTION = str(len(SYMPTOM_OPTIONS) + 2)

def build_symptom_menu() -> list:
    """Builds the symptom menu lines from SYMPTOM_OPTIONS, followed by
    the Remove a Symptom and Done options."""
    symptom_menu = []
    # Menu numbers start from 1, so one is added to each index.
    for index in range(len(SYMPTOM_OPTIONS)):
        option = SYMPTOM_OPTIONS[index]
        symptom_menu.append(f"{index + 1}. {option['label']}")
    symptom_menu.append(f"{REMOVE_SYMPTOM_OPTION}. Remove a Symptom")
    symptom_menu.append(f"{DONE_OPTION}. Done")
    symptom_menu.append("You can also input quit or back")
    return symptom_menu

def chosen_symptom(option: str) -> str | None:
    """Returns the symptom for a numbered option in SYMPTOM_OPTIONS,
    running its follow up question if it has one."""
    chosen_option = SYMPTOM_OPTIONS[int(option) - 1]
    if "ask_function" in chosen_option:
        return chosen_option["ask_function"]()
    return chosen_option["symptom"]

def symptom_handler(previous_symptoms: list) -> list | str:
    """Shows the symptom menu until the user selects Done.

    Works on a copy of previous_symptoms, so the caller's list is never
    changed.

    Returns the new symptom list once the user selects Done, or the
    quit / back command."""
    symptom_list = previous_symptoms.copy()
    header = "Symptoms"
    symptom_menu = build_symptom_menu()
    while True:
        option = dynamic_menu_print(symptom_menu, header)
        symptom = None

        # If user inputs quit or back, return the command.
        if option == QUIT_COMMAND or option == BACK_COMMAND:
            return option

        # For the options in SYMPTOM_OPTIONS,
        # it gets the relevant symptom to add to the list.
        elif option.isdecimal() and 1 <= int(option) <= len(SYMPTOM_OPTIONS):
            symptom = chosen_symptom(option)

        elif option == REMOVE_SYMPTOM_OPTION:
            # removes a symptom from the list.
            symptom_remove(symptom_list)

        elif option == DONE_OPTION:
            # Checks if there is at least one symptom in list,
            # if there isn't, prints a error message
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

        # If symptom is a valid symptom, it appends it to the list.
        if symptom is not None:
            append_list_if_unique(symptom_list, symptom)

def symptom_input(previous_symptoms: list | None) -> tuple:
    """Input function for the symptoms question.

    Runs the symptom menu starting from the previous symptoms, which
    are kept unchanged if the user types quit or back.

    Returns the symptom list as a valid answer, or the quit / back
    command so it is handled like any other answer."""
    symptom_answer = symptom_handler(previous_symptoms or [])
    if symptom_answer == QUIT_COMMAND or symptom_answer == BACK_COMMAND:
        return symptom_answer, None

    # The symptom menu has built in validation, so the list is valid.
    return symptom_answer, True

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

    # If validation_result indicates valid input, then return True.
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
# Set input_function to replace the default typed input for questions
# that need their own input process, such as the symptoms menu.

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
        "validation_function": validate_positive_integer,
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
        "input_function": symptom_input,
        "share_with_ai": True,
    },
    {
        "key": "symptom_onset_days",
        "prompt": (
            "How many days ago did your symptoms start? (e.g. 2, or 0 for today): "
        ),
        "validation_function": validate_decimal_integer,
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
    """This is the main run function. It uses a dictionary approach to 
    move between questions. all_questions variable stores a list of 
    dictionaries, each one containing a question.

    This function cycles through the list of dictionaries to dynamically
    access the correct question based on the current state.

    The output, all_user_responses, will be in structured dictionary
    format."""

    # Initialise state and dictionary to store all answers.
    current_state = 0
    all_user_answers = {}
    # Loop until every question has been answered.
    while current_state < len(ALL_QUESTIONS):
        # Returns the current user answer and its validity.
        current_user_answer, answer_is_valid = input_handler(
            current_state, all_user_answers
        )

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
        # current_state was already set to the previous question
        # in process_quit_or_back().
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

        # If the answers so far mean registration cannot continue,
        # it stops here.
        stop_message = get_stop_message(all_user_answers)
        if stop_message:
            print_message(stop_message)
            return None

    return all_user_answers


def back_to_previous_question(state: int, answers_dict: dict) -> int:
    """Sets inputted state to the state of the previous question, which
    brings the user back to the previous question.

    The previously entered answers are kept in the answers dictionary,
    so questions with an input function (e.g. symptoms) can start from
    them. They are overwritten when the user answers again.
    """

    if state == 0:
        return state

    previous_state = state - 1

    # Skipped questions were never asked, so they are passed over and
    # the user goes back to the last question they actually answered.
    while previous_state > 0 and should_skip(previous_state, answers_dict):
        previous_state -= 1

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
            return
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

def has_emergency_answer(answers_dict: dict) -> bool:
    """Returns True if the user answered Y to any emergency question."""
    for key in EMERGENCY_KEYS:
        if answers_dict.get(key) == "Y":
            return True
    return False

def is_underage(answers_dict: dict) -> bool:
    """Returns True if the user is under MINIMUM_AGE. False if the age
    question has not been answered yet."""
    age = answers_dict.get("age")
    return age is not None and int(age) < MINIMUM_AGE

def get_stop_message(answers_dict: dict) -> str | None:
    """Returns the message to show if the answers so far mean
    registration should stop, otherwise None."""
    if has_emergency_answer(answers_dict):
        return NURSE_ALERT_MESSAGE
    if is_underage(answers_dict):
        return MANUAL_REGISTRATION_MESSAGE
    return None

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

def input_handler(state: int, answers_dict: dict) -> tuple:
    """Gets the user's answer to the question at this state.

    Returns the answer and its validity: True if the input function has
    already validated it, or None if it still needs to be validated."""
    current_question = ALL_QUESTIONS[state]

    # If the question has its own input function, it is run with the
    # previous answer so the user can continue from it.
    input_function = current_question.get("input_function")
    if input_function is not None:
        previous_answer = answers_dict.get(current_question["key"])
        return input_function(previous_answer)

    # For any other question it prints the prompt,
    # and sets the user's input as current_user_answer.
    current_user_answer = input(f"{current_question['prompt']}").upper().strip()
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
    return True

def edit_answer(state: int, answers_dict: dict) -> bool:
    """Asks the question at this state again, and stores the new answer
    if it is valid.

    Returns True if the user typed quit, otherwise False."""
    revised_answer, answer_is_valid = input_handler(state, answers_dict)

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
    types quit, changes consent to N or registration has to stop."""
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

        # If the edited answer means registration cannot continue,
        # it stops here.
        stop_message = get_stop_message(answers_dict)
        if stop_message:
            print_message(stop_message)
            return None

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

def print_box(lines: list, header: str | None = None) -> None:
    """
    Prints the lines inside a box with the dynamic width separator.
    The header is optional; if omitted, only the lines are printed.
    """
    box_width = dynamic_menu_width(lines)
    box_separator = box_width * "-"
    print(box_separator)

    if header:
        print("|" + header.center(box_width - 2) + "|")
        print(box_separator)

    for line in lines:
        print("|" + f" {line}".ljust(box_width - 2) + "|")
    print(box_separator)

def dynamic_menu_print(menu_options: list, menu_header: str | None = None) -> str:
    """
    Prints the menu, based off the menu list,
    with the dynamic width separator.
    Ensures the menu print is properly formatted and centered.
    The header is optional; if omitted, only the options are printed.
    """
    print_box(menu_options, menu_header)
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



def print_message(message: str) -> None:
    """Prints a message to the patient, such as the AI error message."""
    print(message)


# ======================================================================
# RESULT MESSAGE FUNCTIONS
# ======================================================================

# Long messages and explanations are wrapped to this width so the
# result box does not get too wide.
RESULT_WRAP_WIDTH = 70
RESULT_HEADER = "Registration Complete"
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

def wrap_text(text: str, indent: str = "") -> list:
    """Splits text into lines no longer than RESULT_WRAP_WIDTH, adding
    the indent to the start of each line."""
    return textwrap.wrap(
        text,
        RESULT_WRAP_WIDTH,
        initial_indent=indent,
        subsequent_indent=indent,
    )

def build_diagnosis_lines(ai_output: dict, diagnosis: str) -> list:
    """Builds the lines for one diagnosis: its title, explanation and
    medicines. diagnosis is either "primary" or "secondary", matching
    the start of the AI output keys."""
    title = ai_output.get(f"{diagnosis}_diagnosis_ICD11_Title")
    explanation = ai_output.get(f"{diagnosis}_diagnosis_explanation", "")

    lines = [f"{diagnosis.capitalize()} Diagnosis: {title}"]
    lines.extend(wrap_text(explanation, "  "))
    lines.append("  Medicines:")
    for number in [1, 2]:
        medicine = ai_output.get(f"{diagnosis}_diagnosis_medicine_{number}")
        # Skip medicine fields the AI left blank.
        if medicine and medicine.strip():
            lines.append(f"    - {medicine}")
    return lines

def build_result_lines(ai_output: dict, logic_result: dict) -> list:
    """Builds the final message telling the patient what to do next,
    based on the route and queue number from logic_manager.

    Emergency, Doctor and Pharmacist patients get a queue number.
    Retail patients buy medicine on their own, so they get both
    diagnoses and all their medicines instead."""
    route = logic_result.get("route")
    queue_number = logic_result.get("queue_number")
    lines = []

    if queue_number:
        lines.append(f"Your Queue Number: {queue_number}")
        lines.append("")

    # A route without a message should not happen, so the patient is
    # sent to a nurse just in case.
    route_message = ROUTE_MESSAGES.get(route, NURSE_ALERT_MESSAGE)
    lines.extend(wrap_text(route_message))

    if route == "Retail":
        lines.append("")
        lines.extend(build_diagnosis_lines(ai_output, "primary"))
        lines.append("")
        lines.extend(build_diagnosis_lines(ai_output, "secondary"))
        lines.append("")
        lines.extend(wrap_text(RETAIL_DISCLAIMER))

    return lines

def print_result(ai_output: dict, logic_result: dict) -> None:
    """Prints the final message to the patient in a box."""
    print_box(build_result_lines(ai_output, logic_result), RESULT_HEADER)


def print_df_and_reports(data: pd.DataFrame | dict, title: str = ""):
    """
    Print a dataframe or dict that will automatically be formatted into a grid, by row, using the tabulate library.
    If a title is given, it is shown in a box centered over the table.
    """
    # to_markdown only exists on DataFrames, so wrap a flat dict
    # in a list to turn it into a one-row DataFrame.
    if isinstance(data, dict):
        report_df = pd.DataFrame([data])
    else:
        report_df = data

    # Build the table as a string first so its width can be measured
    # before anything is printed.
    grid_table = report_df.to_markdown(index=False, tablefmt="grid", floatfmt=".2f", maxcolwidths=10)

    # Only print a header if a title was given.
    if title:
        # Every line of a grid table is the same length, 
        # so the longest line gives the full width of the table.
        grid_width = max(len(line) for line in grid_table.splitlines())

        # The title box has a "|" on each side, 
        # so the text sits in the space between them.
        inner_width = grid_width - 2

        # Create a border made of "+" corners and "-" fill.
        title_border = "+" + "-" * inner_width + "+"

        # Pad the title so it is centered, then close it with "|" on both sides.
        title_row = "|" + title.center(inner_width) + "|"

        print(title_border)
        print(title_row)

    # The table's own top border acts as the bottom border of the title box.
    print(grid_table)