from datetime import datetime

# get all the medicine names from the AI output
def get_medicines(ai_output): 
    medicines = []

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
        medicine = ai_output.get(key)

        # only add it if there is an medicine
        if medicine:
            medicines.append(medicine)

    # return the list of medicines
    return medicines

# get HSA classification of medicine
def get_classification(medicine, hsa_df):

    # go through every row in the HSA dataset
    for _, row in hsa_df.iterrows():

        # convert the drug name to lowercase
        drug_name= str(row["DrugName"]).lower() 

        # Concert the active ingredient to lowercase
        ingredient= str(row["ActiveIngredients"]).lower() 

        # check if the AI medicine matches either field
        if medicine.lower() in drug_name or medicine.lower() in ingredient:

            # return the HSA classification
            return row["Classification"]

    # return none id medicine is not fouind
    return None

# to decide where the patient should be routed to
def decide_route(all_user_responses, ai_output, hsa_df):

    # AI bypass always routes the patient to a doctor
    if all_user_responses.get("ai_bypass"):
        return "Doctor"

    # get all medicines reccomended by AI
    medicines=get_medicines(ai_output)

    # remember if at least one pharm only medicine is found
    pharmacist_needed = False

    # check each recommended medicine
    for medicine in medicines:

        # get the medicine classification from HSA data
        classification =get_classification(
            medicine,
            hsa_df
        )

        # prescription only medicine requires doctor
        if classification=="Prescription Only":
            return "Doctor"

        # pharmacy only medicine requires pharmacist
        if classification=="Pharmacy Only":
            pharmacist_needed=True

    #if no prescription medicine but a pharmacy only medicine was found
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
        all_user_responses,
        ai_output,
        hsa_df,
):
    """Create the final domain result."""

    # where the patient goes
    route=decide_route(
        all_user_responses,
        ai_output,
        hsa_df
    )

    # get current date and time
    now=datetime.now()

    # AI bypass route ( U queue )
    if all_user_responses.get("ai_bypass"):
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

    # return final resuly
    return result