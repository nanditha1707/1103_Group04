from google import genai
import anthropic
import concurrent.futures
from typing import Any, Callable, Dict
from google.genai.errors import APIError
"""
Function to call the gemini API 
Parameters:
prompt(string): The text prompt or instructions you want to send to Gemini model 
api_key: Your personal Google Gemini API key string, required to authenticate and grant permission to access the service.
model: the model or version of Gemini that you want to use
Variable:
client: Initializes the Google GenAI client object by passing in your api_key. This client handles the network connections and request formatting.
response: Used to Store the full response object received from Google's servers using the command client.models.generate_content(..)
return: Extracts and return just plain generated text through (response.text) back to wherever the function was called.
"""
def call_gemini(
    prompt: str, api_key: str, model: str = "gemini-3.5-flash" 
) -> str: 
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
"""
Function to call the claude API
Parameters Added On:
tokens: This parameter specifies the maximum number of tokens that the model is allowed to use to generate its response.
"""
def call_claude(
    prompt: str, api_key: str, model: str = "claude-sonnet-5", tokens: int = 1024
    ) -> str:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
        model=model,
        max_tokens=tokens,
        messages=[{"role": "user", "content": prompt}],
    )
        return response.content[0].text

"""
Function for AI API Error Handler 
Parameters Added on: 
api_call_func (Callable[[], str]): This is to target AI API function (e.g., call_gemini or call_claude)
api_name: This is for the API node being executed
model_name: This is to specify model name
timeout_seconds: This is the maximum time limit in seconds to wait for an API response before triggering a timeout error.
Dictionary Keys:
success (bool): True if the API call succeeded (200 OK), False if any error occurred
error_type (str | None): The failure category
message (str): The error explanation or status description.
"""

def ai_api_error_handler(
    api_call_func: Callable[[], str],
    api_name: str = "AI API 1",
    model_name: str = "Gemini 3.5 Flash",
    timeout_seconds: int = 60
) -> Dict[str, Any]:
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(api_call_func)
            result_text = future.result(timeout=timeout_seconds)

        if not result_text or not str(result_text).strip():
            error_variable = {
                "success": False,
                "data": None,
                "api_name": api_name,
                "model_name": model_name,
                "error_type": "EMPTY_RESPONSE",
                "status_code": None,
                "message": "Response was empty or blocked by safety filters."
            }
            return error_variable

        return {
            "success": True,
            "data": result_text,
            "api_name": api_name,
            "model_name": model_name,
            "error_type": None,
            "status_code": 200,
            "message": "OK 200"
        }

    except concurrent.futures.TimeoutError:
   
        error_variable = {
            "success": False,
            "data": None,
            "api_name": api_name,
            "model_name": model_name,
            "error_type": "TIMEOUT",
            "status_code": 408,
            "message": f"Execution exceeded {timeout_seconds}s limit."
        }
        return error_variable

    except APIError as e:
       
        status_code = getattr(e, "code", "Unknown")
        raw_msg = getattr(e, "message", str(e))

        if isinstance(status_code, int) and 400 <= status_code < 500:
            error_type = f"Error 4xx ({status_code})"
        elif isinstance(status_code, int) and status_code >= 500:
            error_type = f"Error 5xx ({status_code})"
        else:
            error_type = "API Error"

        error_variable = {
            "success": False,
            "data": None,
            "api_name": api_name,
            "model_name": model_name,
            "error_type": error_type,
            "status_code": status_code,
            "message": raw_msg
        }
        return error_variable

    except Exception as e:
      
        error_variable = {
            "success": False,
            "data": None,
            "api_name": api_name,
            "model_name": model_name,
            "error_type": "SYSTEM_EXCEPTION",
            "status_code": None,
            "message": str(e)
        }
        return error_variable