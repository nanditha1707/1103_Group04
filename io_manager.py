# list containing dictionaries to store all questions, used by run_questions()
all_questions = [
    {
        "key":"consent", 
        "question_number":0,
        "prompt":"Please enter your consent to share your data (Y/N): "
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
        "key":"red_flag_chest_pain",
        "question_number":6,
        "prompt":"Do you have chest pain right now? (Y/N): "
    },
    {
        "key":"red_flag_breathing",
        "question_number":7,
        "prompt":"Are you severely short of breath right now? (Y/N): "
    },
    {
        "key":"red_flag_stroke",
        "question_number":8,
        "prompt":"Do you have sudden weakness or numbness on one side of your body? (Y/N): "
    },
    {
        "key":"self_harm",
        "question_number":9,
        "prompt":"Are you having thoughts of harming yourself? (Y/N): "
    },
    {
        "key":"current_symptoms",
        "question_number":10, 
        "prompt":"Please tell us your current symptoms: "
    },
    {
        "key":"symptom_onset",
        "question_number":11,
        "prompt":"When did your symptoms start? (e.g. 2 days ago): "
    },
    {
        "key":"chronic_conditions",
        "question_number":12, 
        "prompt":"List any long-term medical conditions (e.g. diabetes, high blood pressure), or type 'none': "
    },
    {
        "key":"current_medications",
        "question_number":13, 
        "prompt":"List all medicines you take, including supplements and traditional medicine, or type 'none': "
    },
    {
        "key":"drug_allergies",
        "question_number":14,
        "prompt":"List any drug allergies, or type 'none': "
    },
    {
        "key":"pregnancy",
        "question_number":15,
        "prompt":"Are you currently pregnant? (Y/N): "
    }
]

def run_questions():
    '''Use dictionary approach to move between questions.
    all_questions variable stores a list of dictionaries, each dict containing a question.
    This function cycles through the list of dictionaries to dynamically access the correct 
    question based on the current state.
    
    The output, all_user_responses will be in structured dictionary format.'''

    # initialise state and answers dict to store all responses
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

