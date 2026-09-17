# Project Initial Details

## Group 4

**Team members:** Darrell Lee (2605569), Moe Han, Joana (2604246), Borra Nanditha (2605399), Thach Ke Vin (2604693), and Song En (2605357)

## Main Idea

Hospitals in Singapore are overcrowded. Many patients, particularly those triaged at the less severe “P3” and “P4” level, often come to hospitals where they could instead seek adequate treatment from a pharmacy or a GP clinic. As a result, patients often have to wait long times, often hours, before being able to see a doctor. Our main idea is to build an integrative healthcare system that links patients, hospitals, pharmacies, and General Practitioner (GP) clinics together. Our goal is to make the process for patients to get the appropriate treatment easier and more effective, as well as give patients an accurate idea of how they should proceed. This in turn diverts patients away from the hospitals and reduces stress on their staff and departments. While our system would be valuable to hospitals, it can also be used by other medical facilities.

# 1. Problem Statement and Target Users

## What real-world problem does your application aim to solve?

Singapore's public hospitals are strained by a high volume of low-acuity patients, driven largely by ineffective pre-primary triage at the patient level: patients experiencing severe physical discomfort frequently lack the medical literacy and immediate, evidence-based diagnostic tools required to accurately evaluate the severity of their condition. Conversely. Risk-averse patients default to high-intensity care settings for minor conditions that could be managed effectively via over-the-counter medication or at a local GP clinic. This misallocation of medical resources inflates waiting time for critical patients, increases out-of-pocket costs for the patient, and places unnecessary burdens on public hospitals. Therefore, our system provides to users: a reliable source of information for a quick preliminary diagnosis, to help guide and route patients to get the correct level of care they truly require, helping to reduce the administrative burden and influx of patients seeking out doctor diagnosis for minor ailments like the flu. Medical professionals will also be able to easily access the patient's symptoms and AI diagnosis, allowing them to save the time to get the information from the patient during a consult, and either confirm the diagnosis, or investigate further.

## Who are the intended users of the application?

Potential patients and medical experts are among our users. The potential patients refer to people who are in the polyclinic / hospital / any medical facility, seeking an appointment with a medical professional. This application interface will be accessible to users at certain medical facilities. The interface will retrieve user details similar to the existing walk-in clinic/hospital procedure. Once the required information is retrieved, it will produce a preliminary diagnosis and recommend appropriate actions, like sending them to the pharmacy or a doctor. Medical experts (doctors and pharmacists) will have access to information that the users have submitted. Before forming their own opinions, medical professionals can review the AI findings or use them as a reference. This saves a significant amount of time as doctors and pharmacists do not have to probe the patient from scratch for information – rather all they do is verify the information and clarify any other doubts with the patient. Additionally, if medical professionals disagree with the diagnosis, they can run their own tests and give their own recommendations, as the AI only serves to act as a preliminary diagnosis tool.

# 2. User Inputs

## What information or data will users provide to the system?

Users are to first give consent, then they will be prompted to input their basic information such as their name, NRIC, past medical history (E.g. Conditions and Chronic illnesses, etc.), any known allergies that they have and the current symptoms that they are facing, their pain level that they are currently facing if any and if they have an appointment to a doctor booked already or not and also phone number in order to contact them. As this is a proof-of-concept system that will be implemented with government authorization, we assume that personal information such as NRIC and names can be collected.

# 3. Use of AI

## How will AI be utilized within the application?

The way we will utilize AI is the cognitive core for the program, ergo when user inputs in their medical information, we will form a hypothesis using the medical information coming from the user.

## What outputs, insights, or recommendations will the AI generate from the user inputs?

The user’s data will be fed into the AI, with no personal identifiers to maintain a layer of anonymity. The AI will provide initial insights into potential illnesses based off symptoms, listing out the most likely diseases and any other potential sicknesses, (along with a critical or worst-case scenario), recommend a next course of action, and what drugs should be taken.

The drug recommendation, however, will only be printed if the drug is available over the counter (OTC) or in retail. In a scenario where the recommendation is a prescription only drug, the information will be kept only on our backend and logged.

# 4. Business Rules and Domain Logic

## What business rules, validations, or decision-making logic will be applied to the AI-generated outputs?

1. The buck does not stop with AI, as this is a healthcare system where human lives and health are being decided.
2. The initial AI drug recommendation will be validated against a dataset of drugs that are licensed in Singapore
3. The initial disease diagnosis will be validated against a dataset of all existing diseases and symptoms
4. Prescription drugs can only be prescribed by a doctor, not AI.
5. Pharmacist only drugs can only be issued after assessment by an actual pharmacist, not the AI.
6. All patient records and diagnosis must be logged and stored
7. Risk-based routing
8. User’s drug allergy will be validated against our dataset of drugs
9. Age restrictions must be checked before recommending medication
10. OTC medicine recommendations are for low-risk cases only
11. Existing medical conditions should be checked against drug recommendations
12. Incomplete patient information (e.g. medical history) must block AI recommendations
13. Any patient with chronic conditions must immediately be routed to a doctor.

---
## Github Link: https://github.com/nanditha1707/INF1103-labs