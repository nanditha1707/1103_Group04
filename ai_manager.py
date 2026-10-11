# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import json
import anthropic
import httpx
import pandas as pd
from google import genai
from google.genai import types, errors

FILE_PATH_ICD11 = "datasets/icd_11.csv"
FILE_PATH_HSA = "datasets/ListingofRegisteredTherapeuticProducts.csv"

df1 = pd.read_csv(FILE_PATH_ICD11)
df2 = pd.read_csv(FILE_PATH_HSA)

ai_output = {
    "primary_diagnosis_ICD11_Title": "Viral encephalitis, not elsewhere classified",
    "primary_diagnosis_ICD11_Code": "1C80",
    "secondary_diagnosis_ICD11_Title": "Viral encephalitis, not elsewher classified",
    "secondary_diagnosis_ICD11_Code": "1C0",
    "primary_diagnosis_medicine_1": "Oseltamivir",
    "primary_diagnosis_medicine_2": "Paracetamol",
    "secondary_diagnosis_medicine_1": "Dextromethorphan",
    "secondary_diagnosis_medicine_2": "Chlorpheniramine",
    "ai_confidence_score": 85,
    "refused": "false",
}
# ================================================
# CALL FUNCTIONS FOR CLAUDE AND GEMINI
# ================================================
def call_gemini(prompt, api_key, model="gemini-3.5-flash", tokens=1024):
    """
    Function to call the gemini API.

    Parameters:
        prompt: The text prompt or instructions you want to send to Gemini model.
        api_key: Your personal Google Gemini API key string, required to authenticate
            and grant permission to access the service.
        model: The model or version of Gemini that you want to use.
        tokens: The maximum number of tokens the model is allowed to use to generate
            its response.

    Variables:
        client: Initializes the Google GenAI client object by passing in your api_key.
            This client handles the network connections and request formatting.
        response: Used to store the full response object received from Google's servers
            using the command client.models.generate_content(..).

    Returns:
        Extracts and returns just the plain generated text (response.text) back to
        wherever the function was called.
    """
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=10_000,  # 10s rule done (milliseconds in Gemini)
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(  # this is necessary for gemini due to different sdk
            max_output_tokens=tokens,  # added max tokens
        ),
    )
    return response.text or ""


def call_claude(
    prompt: str, api_key: str, model: str = "claude-sonnet-5", tokens: int = 1024
) -> str:
    """
    Function to call the claude API.

    Parameters Added On:
        tokens: This parameter specifies the maximum number of tokens that the model
            is allowed to use to generate its response.
    """
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

# ================================================
# ERROR CLASSIFICATION FUNCTIONS FOR CLAUDE AND GEMINI
# ================================================
def claude_classify_error(error): 
    """Returns 1, 2 3, or 4:
    1 = give up  400, 413
    2 = retry the same model 500, 504
    3 = switch to a different Claude model 404, 529
    4 = go to gemini 401, 402, 429, 403, 409
    """

    # if the error is a timeout or connection error, we can retry the same model
    if isinstance(error, (anthropic.APITimeoutError, anthropic.APIConnectionError)):
        return 2

    # if the error is a JSON decode error, we can retry the same model
    if isinstance(error, json.JSONDecodeError):
        return 2

    # if the error is an API status error, we can check the status code
    if isinstance(error, anthropic.APIStatusError):
        code = error.status_code

        # model not found, overloaded = switch model (3)
        if code in (404, 529):
            return 3
        # api error, time out ; link back but the timeout error is handled above
        # with timeout error of 10 secs rules = retry (2)
        if code in (500, 504):
            return 2
        # authentication error, billing error, rate limit = switch to gemini
        if code in (401, 402, 429):
            return 4
        # invalid, permission error, conflict error and request too large = fail
        if code in (400, 403, 409, 413):
            return 1

    # if any other else
    print("unknown error code")
    return None


def gemini_classify_error(error): 
    """Returns 1, 2 or 3:
    1 = give up 400,401,403,429,499
    2 = retry the same model 500
    3 = switch to a different Gemini model 404
    """
    # very slow then it will retry
    if isinstance(error, (httpx.TimeoutException, httpx.TransportError)):
        return 2

    # json crash handling (just in case model outputs bad JSON string)
    if isinstance(error, json.JSONDecodeError):
        return 2
    
    #client side error (4xx)
    if isinstance(error, errors.ClientError):
        code = getattr(error, "code", None)
        if code in (400, 401, 403, 429, 499):
            return 1  # Give up
        if code == 404:
            return 3  # 3 -> 1
        return 1  # Default fallback for other 4xx errors

    # server side error (5xx)
    if isinstance(error, errors.ServerError):
        code = getattr(error, "code", None)
        if code == 500:
            return 2  # 2
        if code == 503:
            return 2  # 2 -> 1
        if code == 504:
            return 2  # 2 -> 1
        return 1  # Default fallback for other 5xx server errors

    print("Unknown error code")  # Error code printed out if none of the above conditions are met
    return None
    
# ======================================================================
# VALIDATE DIAGNOSIS, CODE AND MEDICINE
# ======================================================================

# Two series with the column names "Title" and "Code" 
# is pulled from the ICD11 dataset.
dataset_diagnosis = df1["Title"].str.lower()
dataset_code = df1["Code"].str.lower()

# The pandas series with the column name "Productname" 
# is pulled from the HSA medicine dataset.
dataset_medicine = df2["Productname"].str.lower()

def validate_diagnosis_code(diagnosis: str, code: str, label: str) -> bool:
    """The validate_diagnosis_code() function stores the input of 
    three string values named diagnosis, code and label (diagnosis) 
    represent the dictionary(ai_output) value of the diagnosis
    (code) represents the dictionary(ai_output) value of the code 
    (label) represents the level(primary/secondary) of the output 
    Additionally, the result of which output is in the dataset 
    and/or which output is not in the dataset is printed."""

    # False boolean value remains in isvalid_code unless the ai_output 
    # code value finds a match in the "Code" column of df1.
    isvalid_code = False

    for valid_code in dataset_code:
        if code.lower() == valid_code.lower():
            isvalid_code = True
            break

    # False boolean value remains in isvalid_diagnosis unless the 
    # ai_output value finds a match in the "Title" column of df1.
    isvalid_diagnosis = False

    for valid_diagnosis in dataset_diagnosis:
       if diagnosis.lower() == valid_diagnosis.lower():
            isvalid_diagnosis = True
            break

    # Prints the result of a valid match.
    # Else it will indicate which specific data is not found.
    if isvalid_code and isvalid_diagnosis:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are found in the dataset.")
    elif isvalid_diagnosis:
        print(f"The {label} diagnosis: '{diagnosis}' is found in the dataset but the {label} code: '{code}' is not found.")
    elif isvalid_code:
        print(f"The {label} code: '{code}' is found in the dataset but the {label} diagnosis: '{diagnosis}' is not found.")
    else:
        print(f"Both the {label} diagnosis: '{diagnosis}' and the {label} code: '{code}' are not found in the dataset.")

    return isvalid_code, isvalid_diagnosis


def validate_medicine(medicine: str, label: str) -> bool:
    """
    This function has the same concept as validate_diagnosis_code() 
    function but it is to validate medicine instead of disease."""

    isvalid_medicine = False

    # If AI output medicine is in the dataset then set isvalid_medicine
    # flag to True. Else it stays as False.
    for valid_medicine in dataset_medicine:
        if medicine.lower() == valid_medicine.lower():
            isvalid_medicine = True
            break
    
    if isvalid_medicine:
        print(f"The {label} medicine: '{medicine}' is found in the dataset.")
    else:
        print(f"The {label} medcine: '{medicine}'is not found in the dataset.")

    return isvalid_medicine