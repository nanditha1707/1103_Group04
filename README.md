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

Patient records generated while using the application are stored in:

```text
records/patient_records.csv
```

Queried CSV files are stored in:

```text
query/
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
records/
query/
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

Create a file named exactly `.env` in the project directory and add the required API keys:

```text
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
ANTHROPIC_API_KEY=YOUR-ANTHROPIC-API-KEY
```

Do not wrap the API keys in quotation marks.

## Running the Project Locally

Run the application using:

```bash
python main.py
```

## Running with Docker

The recommended method is to run the pre-built Docker image.

### 1. Pull the Docker Image

Preferably use VS Code so that the `.env` file can be created easily.

Open the terminal in the folder where you want the generated files to be stored and run:

```bash
docker pull kevinwuyckens/group04-healthcare:latest
```

This downloads the latest version of the Group 4 healthcare application.

### 2. Create the `.env` File

Create a file named exactly:

```text
.env
```

Add the API keys:

```text
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
ANTHROPIC_API_KEY=YOUR-ANTHROPIC-API-KEY
```

Important:

- Do not use quotes such as `"` or `'` around the API keys because Docker may not read them correctly.
- Ensure the `.env` file is located in the current working directory where the Docker command is being run.

### 3. Run the Docker Container

Run:

```bash
docker run -it --rm --env-file .env -v "${PWD}/records:/app/records" -v "${PWD}/query:/app/query" kevinwuyckens/group04-healthcare:latest
```

The command:

- Runs the application interactively.
- Loads the API keys from `.env`.
- Mounts the local `records/` folder to `/app/records` inside the container.
- Mounts the local `query/` folder to `/app/query` inside the container.
- Automatically removes the temporary Docker container after the application exits.

The following folders will be created in the directory where the command is run:

```text
records/
query/
```

Newly generated patient records will appear under:

```text
records/patient_records.csv
```

Queried CSV files will appear under:

```text
query/
```

The `patient_records.csv` file will contain the existing records from `patient_records_seed.csv` together with any new patient records generated locally.

## Docker Image Build

The Docker image was built and pushed using:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t kevinwuyckens/group04-healthcare:latest --push .
```

The image supports both:

```text
linux/amd64
linux/arm64
```

This allows the application to run on both standard Intel/AMD systems and ARM64 systems such as Apple Silicon Macs.

ARM64 support allows Mac users with Apple Silicon to run the Docker image natively instead of relying on emulation, improving application performance.

## Testing

Run all tests using:

```bash
pytest tests/ -v -s
```

The system can also be manually tested by checking whether:

- Inputs are validated correctly.
- AI output is generated successfully.
- Patients are routed correctly.
- Queue numbers are generated correctly.
- Patient records are saved properly.
- Healthcare professionals can retrieve patient information.
- Medicine reports are generated correctly.
- Patient-type reports are generated correctly.

## GitHub Link

https://github.com/nanditha1707/1103_Group04

## Disclaimer

This project is developed for educational purposes for INF1103 Programming Fundamentals.

The system is a proof-of-concept and should not be used as a replacement for professional medical advice, diagnosis, or treatment.