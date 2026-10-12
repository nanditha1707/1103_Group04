import sys
from pathlib import Path
from datetime import datetime

# allow test file to import from main project folder
sys.path.append(
    str(Path(__file__).parent.parent)
)

from data_manager import (
    export_record,
    get_patient_by_queue,
    display_patient,
    get_medicine_count,
    get_medicine_breakdown,
    get_patient_type_breakdown
)


# get today's date
today = datetime.now().strftime("%Y-%m-%d")


# ============================================================
# TEST DATA - PATIENT 1
# ============================================================

patient_1 = {
    "name": "Darrell",
    "age": "31",
    "gender": "M",
    "red_flag_chest_pain": "N",
    "red_flag_breathing": "N",
    "red_flag_stroke": "N",
    "self_harm": "N",
    "current_symptoms": "Cough, Fever",
    "symptom_onset": "2 days ago",
    "chronic_conditions": "N",
    "current_medications": "N",
    "drug_allergies": "N",
    "priority": False
}

ai_output_1 = {
    "primary_diagnosis_ICD11_Title": "Influenza",
    "primary_diagnosis_ICD11_Code": "1C80",
    "secondary_diagnosis_ICD11_Title": "Upper respiratory infection",
    "secondary_diagnosis_ICD11_Code": "CA00",
    "primary_diagnosis_medicine_1": "Paracetamol",
    "primary_diagnosis_medicine_2": "Oseltamivir",
    "secondary_diagnosis_medicine_1": "",
    "secondary_diagnosis_medicine_2": "",
    "ai_confidence_score": 85
}

logic_result_1 = {
    "queue_number": "D001",
    "date": today,
    "time": "10:00:00",
    "route": "Doctor"
}


# ============================================================
# TEST DATA - PATIENT 2
# ============================================================

patient_2 = {
    "name": "Nanditha",
    "age": "20",
    "gender": "F",
    "red_flag_chest_pain": "N",
    "red_flag_breathing": "N",
    "red_flag_stroke": "N",
    "self_harm": "N",
    "current_symptoms": "Cough",
    "symptom_onset": "1 day ago",
    "chronic_conditions": "N",
    "current_medications": "N",
    "drug_allergies": "N",
    "priority": False
}

ai_output_2 = {
    "primary_diagnosis_ICD11_Title": "Common cold",
    "primary_diagnosis_ICD11_Code": "CA00",
    "secondary_diagnosis_ICD11_Title": "",
    "secondary_diagnosis_ICD11_Code": "",
    "primary_diagnosis_medicine_1": "Paracetamol",
    "primary_diagnosis_medicine_2": "",
    "secondary_diagnosis_medicine_1": "",
    "secondary_diagnosis_medicine_2": "",
    "ai_confidence_score": 80
}

logic_result_2 = {
    "queue_number": "P001",
    "date": today,
    "time": "11:00:00",
    "route": "Pharmacist"
}


# ============================================================
# TEST DATA - PATIENT 3
# ============================================================

patient_3 = {
    "name": "Alex",
    "age": "45",
    "gender": "M",
    "red_flag_chest_pain": "Y",
    "red_flag_breathing": "N",
    "red_flag_stroke": "N",
    "self_harm": "N",
    "current_symptoms": "Chest pain",
    "symptom_onset": "Today",
    "chronic_conditions": "Y",
    "current_medications": "Y",
    "drug_allergies": "N",
    "priority": True
}

ai_output_3 = {
    "primary_diagnosis_ICD11_Title": "Chest pain",
    "primary_diagnosis_ICD11_Code": "MD30",
    "secondary_diagnosis_ICD11_Title": "",
    "secondary_diagnosis_ICD11_Code": "",
    "primary_diagnosis_medicine_1": "",
    "primary_diagnosis_medicine_2": "",
    "secondary_diagnosis_medicine_1": "",
    "secondary_diagnosis_medicine_2": "",
    "ai_confidence_score": 90
}

logic_result_3 = {
    "queue_number": "U001",
    "date": today,
    "time": "12:00:00",
    "route": "Doctor"
}


# ============================================================
# TEST 1 - EXPORT RECORDS
# ============================================================

print("\nTEST 1 - EXPORT RECORDS")
print("-----------------------")

export_record(
    patient_1,
    ai_output_1,
    logic_result_1
)

export_record(
    patient_2,
    ai_output_2,
    logic_result_2
)

export_record(
    patient_3,
    ai_output_3,
    logic_result_3
)

print("PASS - Patient records exported")


# ============================================================
# TEST 2 - GET PATIENT BY QUEUE
# ============================================================

print("\nTEST 2 - GET PATIENT BY QUEUE")
print("-----------------------------")

patient = get_patient_by_queue("D001")

if patient is not None:
    print("PASS - Patient found")
    print("Patient:", patient["name"])
else:
    print("FAIL - Patient not found")


# ============================================================
# TEST 3 - DISPLAY PATIENT
# ============================================================

print("\nTEST 3 - DISPLAY PATIENT")
print("------------------------")

display_patient(patient)


# ============================================================
# TEST 4 - INVALID QUEUE NUMBER
# ============================================================

print("\nTEST 4 - INVALID QUEUE NUMBER")
print("-----------------------------")

invalid_patient = get_patient_by_queue("D999")

if invalid_patient is None:
    print("PASS - Invalid queue number returned no patient")
else:
    print("FAIL - Incorrect patient returned")


# ============================================================
# TEST 5 - SPECIFIC MEDICINE COUNT
# ============================================================

print("\nTEST 5 - SPECIFIC MEDICINE COUNT")
print("--------------------------------")

medicine_count = get_medicine_count(
    today,
    "Paracetamol"
)

print("Paracetamol count:", medicine_count)

if medicine_count >= 2:
    print("PASS - Medicine count is correct")
else:
    print("FAIL - Medicine count is incorrect")


# ============================================================
# TEST 6 - MEDICINE NOT ISSUED
# ============================================================

print("\nTEST 6 - MEDICINE NOT ISSUED")
print("----------------------------")

medicine_count = get_medicine_count(
    today,
    "Aspirin"
)

if medicine_count == 0:
    print("PASS - Aspirin was not issued")
else:
    print("FAIL - Incorrect medicine count")


# ============================================================
# TEST 7 - MEDICINE BREAKDOWN
# ============================================================

print("\nTEST 7 - MEDICINE BREAKDOWN")
print("---------------------------")

medicine_breakdown = get_medicine_breakdown(
    today
)

if medicine_breakdown:
    print("PASS - Medicine breakdown returned")

    for medicine, count in medicine_breakdown.items():
        print(medicine, "-", count)

else:
    print("FAIL - No medicine breakdown returned")


# ============================================================
# TEST 8 - PATIENT TYPE BREAKDOWN
# ============================================================

print("\nTEST 8 - PATIENT TYPE BREAKDOWN")
print("-------------------------------")

patient_breakdown = get_patient_type_breakdown(
    today
)

print("Emergency:", patient_breakdown["Emergency"])
print("Doctor:", patient_breakdown["Doctor"])
print("Pharmacy:", patient_breakdown["Pharmacy"])
print("Retail:", patient_breakdown["Retail"])

print("PASS - Patient type breakdown returned")