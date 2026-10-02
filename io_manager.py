import re

QUIT_SIGNAL = -99

# list containing dictionaries to store all questions, used by run_questions()
ALL_QUESTIONS = [
    {
        "key":"consent", 
        "question_number":0,
        "prompt":"Do you consent to sharing your data (Y/N): "
    },
    {
        "key":"name", 
        "question_number":1,
        "prompt":"Enter your Name: "
    },
    {
        "key":"nric",
        "question_number":2, 
        "prompt":"Enter your NRIC: "
    },
    {
        "key":"gender",
        "question_number":3, 
        "prompt":"Enter your Gender [M/F]: "
    },
    {
        "key":"age",
        "question_number":4, 
        "prompt":"Enter your Age: "
    },
    {
        "key":"phone_number", 
        "question_number":5,
        "prompt":"Please enter your phone number: "
    },
    {
        "key":"pregnancy",
        "question_number":6,
        "prompt":"Are you currently pregnant? (Y/N): "
    },

    {
        "key":"red_flag_chest_pain",
        "question_number":7,
        "prompt":"Are you currently experiencing chets pain? (Y/N): "
    },
    {
        "key":"red_flag_breathing",
        "question_number":8,
        "prompt":"Are you severely short of breath right now? (Y/N): "
    },
    {
        "key":"red_flag_stroke",
        "question_number":9,
        "prompt":"Do you have sudden weakness or numbness on one side of your body? (Y/N): "
    },
    {
        "key":"self_harm",
        "question_number":10,
        "prompt":"Are you having thoughts of harming yourself? (Y/N): "
    },
    {
        "key":"current_symptoms",
        "question_number":11, 
        "prompt":"Please tell us your current symptoms: "
    },
    {
        "key":"symptom_onset",
        "question_number":12,
        "prompt":"When did your symptoms start? (e.g. 2 days ago): "
    },
    {
        "key":"chronic_conditions",
        "question_number":13, 
        "prompt":"Are you suffering from any chronic conditions? (Y/N): "
    },
    {
        "key":"current_medications",
        "question_number":14, 
        "prompt":"Are you currently on any medication? (Y/N): "
    },
    {
        "key":"drug_allergies",
        "question_number":15,
        "prompt":"List any drug allergies, or type 'none': "
    }
]

def validate_consent(input : str, state : int):
    """
    Dedicated function to validate the consent question input
    Parameters:
    input(string): "Y" or "N" input.
    validated_flag(bool): Boolean flag indicating whether or not the file has been validated, main value returned
    state(int): represents the current step in the questionare, needed for other linked functions and to terminate program
    Input
    """
    if input == "Y":
        validated_flag = True
        return validated_flag, state
    elif input == "N":
        # Program cannot store data and make AI analysis without user consent
        print("You have not given your consent, as such, we are unable to process you into the system.")
        validated_flag= True
        # Sets the state to the exit signal to tell program to stop running its current questionare
        state = QUIT_SIGNAL
        return validated_flag, state
    else:
        print("This is not a valid response, please only enter Y or N!")
        validated_flag= False
        return validated_flag, state

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
            break
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

        # validates the response before storing it
        validated_flag, state = validate_orchestator(response, state)

        # invalid response, do not store it and ask the same question again
        if not validated_flag:
            continue

        # user typed QUIT or refused consent, stop asking questions
        if response == "QUIT" or state == QUIT_SIGNAL:
            break

        # user typed BACK, go to the previous question (unless already on the first one)
        if response == "BACK":
            if state > 0:
                state -= 1
            continue

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

