# list containing dictionaries to store all questions, used by run_questions()
all_questions = [
    {
        "key":"consent", 
        "question_number":0,
        "prompt":"Please enter your consent to share your data with the AI pharmacist (Y/N): "
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
        "question_number":3, 
        "prompt":"Enter your Age: "
    },
    {
        "key":"phone_number", 
        "question_number":4,
        "prompt":"Please enter your phone number"
    },
    {
        "key":"chronic_conditions",
        "question_number":5, 
        "prompt":"Do you have any chronic conditions?: "
    },
    {
        "key":"current_medications",
        "question_number":6, 
        "prompt":"Are you on any medication prescribed by a doctor: "
    },
    {
        "key":"current_symptoms",
        "question_number":7, 
        "prompt":"Please tell us your current symptoms: "
    }
]

def run_questions():
    '''Use dictionary approach to move between questions.
    all_questions variable stores a list of dictionaries, each dict containing a question.
    This function cycles through the list of dictionaries to dynamically access the correct 
    question based on the current state.
    
    The output, all_user_responses will be in structured dictionary format.'''

    # initialise state and answers dict to store all responses.
    state = 0
    all_user_responses = {}

    while state < len(all_questions):

        # this tells which dictionary to point at
        # intiially, all_questions[0] since state = 0, which refers to the consent dictionary
        question_index = all_questions[state]
        
        # ask the "prompt" value of the currently selected dictionary
        response = input(f"{question_index["prompt"]}")

        # stores the answer in the answers dictionary with the corresponding "key"
        all_user_responses[question_index["key"]] = response

        # increments state by 1 to move onto the next question, till all questions completed
        state += 1

    # return the final dictionary with all answers to the questions
    return all_user_responses

run_questions()

