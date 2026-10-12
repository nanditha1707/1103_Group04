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

# ======================================================================
# CORE FUNCTIONS
# ======================================================================

def main_menu():
    header = "Main Menu"
    main_menu_option= io.dynamic_menu_print(MAIN_MENU_OPTIONS, header)
    if main_menu_option not in ["1","2","3"]:
        error = "This is not a valid option!"
        io.print_text(error)
    elif main_menu_option == "1":
        all_answers = io.run_questions()
        if all_answers == None or len(all_answers) < len(io.ALL_QUESTIONS)+1:
            return None
        elif len(all_answers) == len(io.ALL_QUESTIONS)+1:
            confirmed = io.confirm_inputs(all_answers)
            if confirmed:
                confirm_message = "Thank you for confirming your inputs."
                print(confirm_message)
                return all_answers
            else:
                error = io.REG_EXIT_MESSAGE
                io.print_text(error)
    elif main_menu_option == "2":
        # WIP
    elif main_menu_option == "3":
        inputted_pass=input("Enter the exit code here: ")
        if inputted_pass == ADMIN_PASSWORD:
            io.print_text(MENU_EXIT_MESSAGE)
            return io.QUIT_SIGNAL
        else:
            error="This is not the right password!"

# load the ICD and HSA datasets once, when the program starts
icd_df, hsa_df = data.get_cleaned_datasets()

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
    logic_result = logic.process_result(answers, ai_output, hsa_df)

    # 4. Data manager: save the completed record to patient_records.csv
    is_export=data.export_record(answers, ai_output, logic_result)
    if not is_export:
        error=("The program has encountered an error."
              "Please approach a nurse or clerk for manual registration.")
        io.print_text(error)
