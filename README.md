# 1103_P8_G4

INF1103 Programming Fundamentals project Group 4

**Team Members:** Darrell Lee (2605569), Moe Han (2605699), Joana (2604246), Borra Nanditha (2605399), Thach Ke Vin (2604693), and Song En (2605357)

## Main Idea

Hospitals in Singapore can experience long waiting times due to patients seeking hospital care for conditions that may be manageable through a GP clinic, pharmacy, or retail medication.

Our project is an **AI-assisted patient triage and routing system** that helps patients understand the most suitable next step based on their symptoms and medical information.

The system collects and validates patient information, uses AI to generate a preliminary diagnosis and medicine recommendations, validates the results against healthcare datasets, and routes the patient to one of the following:

- Emergency
- Doctor
- Pharmacist
- Retail

The system also stores patient records so that healthcare professionals can retrieve and review the patient's information and AI-generated results.

## Target Users

The main users of the system are:

- Patients seeking medical assistance.
- Doctors.
- Pharmacists.
- Other healthcare professionals.

Patients use the system to provide their symptoms and medical information before receiving a preliminary diagnosis and routing recommendation.

Healthcare professionals can access stored patient records and review the information before making their own assessment.

## Features

### Patient Registration

- Collects patient information.
- Validates user inputs.
- Checks for emergency and priority symptoms.
- Allows patients to review their information.

### AI Diagnosis

- Uses Gemini and Claude APIs.
- Generates primary and secondary diagnoses.
- Suggests possible medicines.
- Provides an AI confidence score.
- Validates diagnoses and medicines against healthcare datasets.

### Patient Routing

Patients may be routed to:

- Emergency
- Doctor
- Pharmacist
- Retail

Queue numbers are generated when required.

Example:

```text
U001
D001
P001
```

### Data Management

The Data Manager is responsible for:

- Loading and cleaning the ICD-11 dataset.
- Loading and cleaning the HSA medicine dataset.
- Saving patient records.
- Searching for patient records.
- Generating medicine and patient-type breakdowns.

Patient records are stored in:

```text
datasets/patient_records.csv
```

## Business Rules

Some of the main rules used by the system include:

1. AI output must be validated before it is used.
2. Medicine recommendations must be checked against the HSA dataset.
3. Diagnoses must be checked against the ICD-11 dataset.
4. Prescription Only medicines require a doctor.
5. Pharmacy Only medicines require a pharmacist.
6. Priority and emergency patients are given urgent routing.
7. Patient records and diagnoses are stored for future reference.

## Project Structure

```text
main.py
io_manager.py
ai_manager.py
logic_manager.py
data_manager.py
datasets/
tests/
requirements.txt
dockerfile
```

## Technologies Used

- Python
- Pandas
- NumPy
- Google Gemini API
- Anthropic Claude API
- Docker
- GitHub
- Pytest
- Pylint

## Setup

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add the required API keys:

```text
GEMINI_API_KEY="YOUR-GEMINI-API-KEY"
ANTHROPIC_API_KEY="YOUR-ANTHROPIC-API-KEY"
```

## Running the Project

Run the application using:

```bash
python main.py
```

## Running with Docker

Build the Docker image:

```bash
docker build -f dockerfile -t 1103-group04 .
```

Run the container:

```bash
docker run --env-file .env -it 1103-group04
```

## Testing

Run the tests using:

```bash
pytest
```

The system can also be manually tested by checking whether:

- Inputs are validated correctly.
- AI output is generated successfully.
- Patients are routed correctly.
- Queue numbers are generated correctly.
- Patient records are saved properly.

## GitHub Link

https://github.com/nanditha1707/1103_Group04

## Disclaimer

This project is developed for educational purposes for INF1103 Programming Fundamentals.

The system is a proof-of-concept and should not be used as a replacement for professional medical advice, diagnosis, or treatment.