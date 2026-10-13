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
def option_handler(option:str):
    error_message = io.validate_option(option)
    if error_message:
        io.print_text(error_message)
        return False
    else:
        return True
    
def healthcare_portal_routing(option:str):
    option = int(option)
    today = data.get_current_date()
    if option == 1:
        filter_option= io.dynamic_menu_print(FILTER_OPTIONS)
        is_valid = option_handler(filter_option)
        if is_valid:
            filter= data.get_patient_filter(filter_option)
            queue = input("Enter the Patient's Queue Number here.")
            query_response= data.get_patient_by_queue(queue, filter, today)
            if not query_response.empty:
                io.print_df(query_response)
            else:
                error ="There is no such patient, please enter a valid queue number!"
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
        is_valid= option_handler(choice)
        if  is_valid:
            healthcare_portal_routing(choice)

    elif main_menu_option == "3":
        inputted_pass=input("Enter the exit code here: ")
        if inputted_pass == ADMIN_PASSWORD:
            io.print_text(MENU_EXIT_MESSAGE)
            return io.QUIT_SIGNAL
        else:
            error="This is not the right password!"

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()
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
    print(previous_records_df) #DEBUGGING
