# 1103_P8_G4

INF1103 Programming Fundamentals project Group 4

**Team Members:** Darrell Lee (2605569), Moe Han (2605699), Joana (2604246), Borra Nanditha (2605399), Thach Ke Vin (2604693), and Song En (2605357)

## Important run steps

For security reasons, we will not be pasting any keys here as the repo
is public. To obtain the keys needed to run the project, please look in 
the Appendix in the engineering report.

Docker run:
docker run -it --rm --env-file .env -v "${PWD}/query:/app/query" kevinwuyckens/group04-healthcare:latest

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
PR001
```

`U` is used for Emergency, `D` for Doctor, `P` for Pharmacist and `PR` for Retail.

### Data Management

The Data Manager is responsible for:

- Loading and cleaning the ICD-11 dataset.
- Loading and cleaning the HSA medicine dataset.
- Loading the symptom list (from the NIH UMLS Metathesaurus) used to match symptoms typed under "Other Symptoms".
- Encrypting and saving patient records.
- Finding and decrypting patient records.
- Counting the records used for the medicine and patient-type reports.

The Healthcare Professional Portal in `app/` handles the search menus (`app/queries/`) and turns the counts into reports (`app/reports/`).

Patient records are stored in the `patient_records` table of a cloud PostgreSQL database hosted on Neon. Searches and reports query the database directly, so they always include records saved by other users.

Personal details such as name, NRIC, birthdate, phone number and symptoms are encrypted with a Fernet key (`PATIENT_DATA_ENCRYPTION_KEY`) before they are saved, and decrypted when they are read back.

The table name can be changed with the optional `PATIENT_RECORDS_TABLE` environment variable. If it is not set, `patient_records` is used.

Query results that are too wide for the terminal are exported as CSV files to:

```text
query/
```

These files hold decrypted patient data, so they are temporary. They are deleted when the program exits including through Ctrl+C or an error. Any file left behind because the program was force-closed is deleted the next time the program starts. A file that is still open in another program (e.g. Excel) cannot be deleted and is removed on the next run instead.

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
app/
io_manager/
ai_manager/
logic_manager/
data_manager/
typedefs/
datasets/
tests/
run_tests.py
requirements.txt
.env.example
dockerfile
```

The `query/` folder is not part of the repository. It is created when the first query is exported.

## Technologies Used

- Python
- Pandas
- NumPy
- PostgreSQL (Neon) with psycopg
- cryptography (Fernet encryption)
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

Create a file named exactly `.env` in the project directory. The easiest way is to copy `.env.example`, which already lists every key and where to get the API keys. Then add the required API keys, the cloud database URL, the encryption key and the admin password:

```text
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
ANTHROPIC_API_KEY=YOUR-ANTHROPIC-API-KEY
POSTGRESQL_CLOUD_DATABASE_URL=YOUR-DATABASE-URL
PATIENT_DATA_ENCRYPTION_KEY=YOUR-ENCRYPTION-KEY
ADMIN_PASSWORD=YOUR-ADMIN-PASSWORD
```
`ADMIN_PASSWORD` is asked for before the Healthcare Professional Portal opens and before the program exits.
The program will not start without it.
In a real world implementation, the fernet encryption key would not be given like this.
However, for the purposes of testing and demonstration, we have provided it.
Do not wrap the values in quotation marks.

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

Add the API keys, the cloud database URL, the encryption key and the admin password. You can find the keys needed
in the Engineering Report:

```text
GEMINI_API_KEY=YOUR-GEMINI-API-KEY
ANTHROPIC_API_KEY=YOUR-ANTHROPIC-API-KEY
POSTGRESQL_CLOUD_DATABASE_URL=YOUR-DATABASE-URL
PATIENT_DATA_ENCRYPTION_KEY=YOUR-ENCRYPTION-KEY
ADMIN_PASSWORD=YOUR-ADMIN-PASSWORD
```

Important:

- Do not use quotes such as `"` or `'` around the values because Docker may not read them correctly.
- Ensure the `.env` file is located in the current working directory where the Docker command is being run.
- Without `POSTGRESQL_CLOUD_DATABASE_URL`, patient records cannot be saved or queried.
- Without `ADMIN_PASSWORD`, the program will not start.

### 3. Run the Docker Container

Run:

```bash
docker run -it --rm --env-file .env -v "${PWD}/query:/app/query" kevinwuyckens/group04-healthcare:latest
```

The command:

- Runs the application interactively.
- Loads the API keys, database URL, encryption key and admin password from `.env`.
- Mounts the local `query/` folder to `/app/query` inside the container.
- Automatically removes the temporary Docker container after the application exits.

Patient records are saved to and read from the cloud PostgreSQL database, so no `records/` folder is needed. Every container connected to the same database sees the same, up-to-date records.

Queried CSV files will appear in the `query/` folder, which is created in the directory where the command is run:

```text
query/
```

Open them while the program is running. They are deleted when the program exits.

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

ARM64 support allows Mac users with Apple Silicon to run the Docker image natively instead of relying on emulation improving application performance
on Apple silicon Macs.

## Testing

### Run Tests Locally

To run all automated tests locally, use:

```bash
pytest tests/ -v -s
```

### Run Tests Inside Docker

To run the automated test suite inside the Docker container, use:

```bash
docker run --rm kevinwuyckens/group04-healthcare:latest python run_tests.py
```

The `run_tests.py` script runs the automated test cases inside the Docker image.

These tests verify the core application logic, including `logic_manager`, using hardcoded sample AI responses so that the tests can run independently without requiring a live Gemini or Claude API connection.


## GitHub Link

https://github.com/nanditha1707/1103_Group04

## Disclaimer

This project is developed for educational purposes for INF1103 Programming Fundamentals.

The system is a proof-of-concept and should not be used as a replacement for professional medical advice, diagnosis, or treatment.