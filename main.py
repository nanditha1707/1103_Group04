# ======================================================================
# IMPORT FUNCTIONS AND CONSTANTS
# ======================================================================
import ai_manager as ai
import data_manager as data
import io_manager as io
import logic_manager as logic

ADMIN_PASSWORD = "Password"
MENU_EXIT_MESSAGE = "Admin Password Inputted, Exiting Program Now!"
MAIN_MENU_OPTIONS = ["1. Patient Registration",
                     "2. Healthcare Professional Portal",
                     "3. Exit"]
HEALTHCARE_PORTAL_OPTIONS = [
    "1. Query Current Patient Information",
    "2. Query Past Patient Information",
    "3. Reports",
                             ]
FILTER_OPTIONS =[
    "1. Patient Information", 
    "2. Medical Information", 
    "3. AI Ouput Information", 
    "4. All Records"
                 ]


# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def patient_query_handler(date) ->str | None:
    error = None
    filter_option= io.dynamic_menu_print(FILTER_OPTIONS)
    option_error = io.validate_option(filter_option)
    if option_error is None:
        filter= data.get_patient_filter(filter_option)
        if filter is None:
            error = "This is not a valid option number!"
        else:
            queue = input("Enter the Patient's Queue Number here.").strip().upper()
            # Load the latest records so patients registered this session are found.
            records = data.load_records()
            query_response= data.get_patient_by_queue(records, queue, filter, date)
            if query_response is not None and not query_response.empty:
                io.print_df(query_response)
            else:
                error ="There is no such patient, please enter a valid queue number!"
    else:
        error = option_error
    return error

def healthcare_portal_routing(option:str):
    option = int(option)
    error = None
    today = data.get_current_date()
    if option == 1:
        error = patient_query_handler(today)
    if option == 2:
        datetime_answer = str(input("Enter the Date here. (YYYY-MM-DD)"))
        error_message = io.validate_date(datetime_answer)
        if error_message is None:
            error_message = patient_query_handler(datetime_answer)

    if error:
        io.print_text(error)




def main_menu():
    header = "Main Menu"
    main_menu_option= io.dynamic_menu_print(MAIN_MENU_OPTIONS, header)
    if main_menu_option not in ["1","2","3"]:
        error = "This is not a valid option!"
        io.print_text(error)
    elif main_menu_option == "1":
        all_answers = io.run_questions()
        if all_answers is None:
            return None
        else:
            confirmed = io.confirm_inputs(all_answers)
            if confirmed:
                confirm_message = "Thank you for confirming your inputs."
                print(confirm_message)
                return all_answers
            else:
                error = io.REG_EXIT_MESSAGE
                io.print_text(error)
    elif main_menu_option == "2":
        choice=io.dynamic_menu_print(HEALTHCARE_PORTAL_OPTIONS)
        option_error= io.validate_option(choice)
        if option_error is None:
            healthcare_portal_routing(choice)
        else:
            io.print_text(option_error)

    elif main_menu_option == "3":
        inputted_pass=input("Enter the exit code here: ")
        if inputted_pass == ADMIN_PASSWORD:
            io.print_text(MENU_EXIT_MESSAGE)
            return io.QUIT_SIGNAL
        else:
            error="This is not the right password!"
            io.print_text(error)

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()
# Copy the starter patient records on the first run
data.create_records_file_if_missing()
#Load the previous entry records
previous_records_df= data.load_records()

while True:
    # 1. I/O manager: collect the patient's answers
    answers=main_menu()
    if answers == io.QUIT_SIGNAL:
        break
    if answers is None:
        continue

    # Filter answers so only non-personal information goes to the AI.
    answers_filtered = io.filter_answers(answers)

    # 2. AI manager: get a diagnosis and medicines
    ai_output = ai.get_ai_output(answers_filtered)

    # get_ai_output returns a dictionary when every AI model failed.
    # The key is "error". The value of the key is the message telling 
    # patients to seek assistance.
    if "error" in ai_output:
        io.print_text(ai_output["error"])
        continue

    # 3. Logic manager: decide and print the route and queue number
    logic_result = logic.process_result(ai_output, hsa_df)

    # 4. Data manager: save the completed record to patient_records.csv
    is_export=data.export_record(answers, ai_output, logic_result, previous_records_df)
    if not is_export:
        error=("The program has encountered an error."
              "Please approach a nurse or clerk for manual registration.")
        io.print_text(error)
    else:
        # 5. I/O manager: tell the patient what to do next
        io.print_result(ai_output, logic_result)
