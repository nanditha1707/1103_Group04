from datetime import datetime

# get all the medicine names from the AI output
def get_medicines(ai_output): 
    ai_medicines = []

    # keys where the medicines are stored in the AI output
    medicine_keys =[
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2", 
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    ]

    # go through each medicine key
    for key in medicine_keys:

        # get the medicine stored under the key
        ai_medicine = ai_output.get(key)

        # only add it if there is an medicine
        if ai_medicine:
            ai_medicines.append(ai_medicine)

    # return the list of medicines
    return ai_medicines

# get HSA classification of medicine
def get_classification(ai_medicine, hsa_df):

    # go through the HSA dataset one row at a time. The row number is used
    # to get the drug name and active ingredient from that same row.
    for row in range(len(hsa_df)):
        drug_name = hsa_df["DrugName"][row]
        ingredient = hsa_df["ActiveIngredients"][row]

        # check if the AI medicine matches either field
        if ai_medicine in drug_name or ai_medicine in ingredient:

            # return the HSA classification from the same row
            return hsa_df["Classification"][row]

    # return None if medicine is not found
    return None

# check if the AI flagged the patient as an emergency
def is_emergency(ai_output):

    # keys where the AI explains each diagnosis
    explanation_keys = [
        "primary_diagnosis_explanation",
        "secondary_diagnosis_explanation"
    ]

    # go through each explanation
    for key in explanation_keys:

        # emergency if the explanation contains the word EMERGENCY
        if "EMERGENCY" in str(ai_output.get(key, "")):
            return True

    return False

# to decide where the patient should be routed to
def decide_route(answers_dict, ai_output, hsa_df):

    # AI flagged an emergency, this overrides every other route
    if is_emergency(ai_output):
        return "EMERGENCY"

    # AI bypass always routes the patient to a doctor
    if answers_dict.get("priority"):
        return "Doctor"

    # without HSA data the medicines cannot be checked, so see a doctor
    if hsa_df is None:
        return "Doctor"

    # get all medicines reccomended by AI
    ai_medicines=get_medicines(ai_output)

    # remember if at least one pharm only medicine is found
    pharmacist_needed = False

    # check each recommended medicine
    for ai_medicine in ai_medicines:

        # get the medicine classification from HSA data
        classification = get_classification(ai_medicine, hsa_df)

        # prescription only medicine requires doctor
        if classification == "Prescription Only":
            return "Doctor"

        # pharmacy only medicine requires pharmacist
        if classification=="Pharmacy Only":
            pharmacist_needed=True

    # if no prescription medicine but a pharmacy only medicine was found
    if pharmacist_needed:
        return "Pharmacist"

    # otherwise patient can go to retail
    return "Retail"

# generate next queue number based on routing
def get_queue_number(queue_type):

    # get todays date
    today=datetime.now().strftime("%Y-%m-%d")

    # all queue counters start at 0
    doctor_count=0
    pharmacist_count=0
    bypass_count=0

    try:
        # open queue file
        with open("queue_number.txt", "r", encoding="utf-8") as file:

            # read saved file
            data =file.read().strip()

       # split the saved date, and counters
        saved_date,doctor,pharmacist,bypass=data.split(",")

        # same queue number, if it it still the same day
        if saved_date==today:
            doctor_count=int(doctor)
            pharmacist_count=int(pharmacist)
            bypass_count=int(bypass)

    # if queue file is not found, start all queues from 0
    except FileNotFoundError:
        pass

    queue_number = None

    # doctor queue
    if queue_type =="Doctor":
        doctor_count +=1
        queue_number = f"D{doctor_count:03d}"

    # pharmacist queue
    elif queue_type =="Pharmacist":
        pharmacist_count +=1
        queue_number =f"P{pharmacist_count:03d}"

    # Urgent AI bypass queue
    elif queue_type=="Bypass":
        bypass_count +=1
        queue_number =f"U{bypass_count:03d}"

    # save updated file
    with open("queue_number.txt", "w", encoding="utf-8") as file:

        file.write(
            today + ","
            + str(doctor_count) + ","
            + str(pharmacist_count) + ","
            + str(bypass_count)
        )

    # return generated queue number 
    return queue_number

# final domain 
def process_result(
        answers_dict,
        ai_output,
        hsa_df,
):
    """Create the final domain result."""

    # where the patient goes
    route=decide_route(
        answers_dict,
        ai_output,
        hsa_df
    )

    # get current date and time
    now=datetime.now()

    # AI bypass route ( U queue )
    if answers_dict.get("priority"):
        queue_number =get_queue_number("Bypass")

    # docter route ( D queue )
    elif route =="Doctor":
        queue_number =get_queue_number("Doctor")

    # pharmacist route ( P queue )
    elif route =="Pharmacist":
        queue_number =get_queue_number("Pharmacist")

    # retail does not get a queue number
    else:
        queue_number = None

    # store final results
    result ={
        "queue_number": queue_number,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "route": route
    }

    # return final result
    return result