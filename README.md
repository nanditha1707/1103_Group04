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


### Test Cases

There are 49 automated tests across 12 files in the `tests/` folder.

#### `test_ai_manager.py`

- `test_falls_back_to_next_provider`: if Claude fails because its key is invalid the app moves on to Gemini and uses Gemini's diagnosis.
- `test_every_model_fails`: if every AI model fails the app returns the "contact support" error.

#### `test_data_manager.py`

- `test_join_symptoms`: a list of symptoms is saved as one text value, like "COUGH, FEVER, HEADACHE".
- `test_record_columns`: the app reports the full correct list of record columns.
- `test_get_patient_by_queue`: looking up a queue number on a date returns that patient's details.
- `test_patient_not_found`: an unknown queue number returns an empty result.
- `test_export_record`: a full registration is saved as one record with the right values, and extras like consent are left out.
- `test_get_patients_by_date`: all patients on a date are returned, with time and queue number added so the rows can be told apart.
- `test_get_patients_by_date_keeps_existing_columns`: when every column is requested, time and queue number are not added a second time.

#### `test_dataset_cleaning.py`

- `test_clean_icd_data`: the diagnosis code list is trimmed and uppercased, and duplicates and blank rows are removed.
- `test_clean_hsa_data`: the medicine list is trimmed and uppercased, and duplicates are removed.

#### `test_encryption.py`

- `test_fernet_round_trip`: encrypted data decrypts back with the right key and cannot be read with the wrong one.
- `test_record_encryptor_sensitive_columns`: only sensitive fields are encrypted, and they decrypt correctly afterwards.

#### `test_healthcare_portal.py`

- `test_current_patient_found`: searching for todays patient by queue number shows their details.
- `test_patient_not_found`: an unknown queue number shows the "patient not found" message.
- `test_current_patient_uses_today`: a search for current patients uses today's date.
- `test_past_patient_uses_selected_date`: a search for past patients uses the date the user picked.
- `test_patient_query_database_down`: if the database cannot be reached a database error message is shown.
- `test_all_patients_on_date`: listing all patients on a date shows every patient.
- `test_all_patients_none_on_date`: a date with no patients shows the "no records" message.
- `test_invalid_query_scope`: an invalid choice between one patient and all patients shows an error and does not search.

#### `test_key_verifier.py`

- `test_correct_key_passes`: the startup check passes when the encryption key matches the database.
- `test_wrong_key_fails`: the startup check warns when the encryption key does not match.
- `test_no_check_value_to_verify`: the startup check warns when the database cannot be reached or has no check value saved.

#### `test_logic_manager.py`

- `test_all_retail_medicines`: a patient who medicines are all over-the-counter goes to Retail.
- `test_pharmacy_medicine_overrides_retail`: one pharmacy-only medicine sends the patient to the Pharmacist.
- `test_prescription_medicine_overrides_other_routes`: one prescription medicine sends the patient to the Doctor.
- `test_emergency_overrides_medicine_routing`: an emergency goes to Emergency, whatever the medicines are.

#### `test_main_menu.py`

- `test_successful_patient_registration`: a full registration saves the record, gives a queue number and does not send the name or NRIC to the AI.
- `test_invalid_main_menu_option`: an invalid menu choice shows an error.
- `test_healthcare_portal_selected`: the right password opens the healthcare portal.
- `test_healthcare_portal_wrong_password`: a wrong portal password is rejected and no data is looked up.
- `test_correct_exit_password`: the right exit password closes the program.
- `test_wrong_exit_password`: a wrong exit password keeps the program running.

#### `test_postgres_database.py`

- `test_database_down`: if the database cannot be reached, looking up and saving records fail without crashing.
- `test_missing_database_url`: if the database URL is missing or empty the app shows a "no database URL was given" error instead of crashing.
- `test_invalid_database_url`: if the database URL is badly formatted, the app shows an error instead of crashing.

#### `test_query_export.py`

- `test_clear_deletes_exported_queries`: exported search results are deleted at exit, so no decrypted patient data stays on disk.

#### `test_registration.py`

- `test_normal_female_registration`: a female patient completes registration and is asked the pregnancy question.
- `test_normal_male_registration`: a male patient completes registration and the pregnancy question is skipped.
- `test_gender_changed_to_female_needs_pregnancy_answer`: if a male patient changes their gender to F on the confirmation screen, they must answer the pregnancy question before they can confirm their inputs.
- `test_no_consent`: a patient who does not consent has registration stopped.
- `test_emergency_chest_pain`: chest pain stops registration and sends the patient to a nurse.
- `test_underage_patient`: an underage patient is sent to manual registration.

#### `test_reports.py`

- `test_medicine_count`: counts how many times one medicine was given out on a date.
- `test_medicine_not_issued`: a medicine that was not given out returns an empty count.
- `test_medicine_breakdown`: counts every medicine given out on a date.
- `test_patient_type_breakdown`: counts patients by route (Doctor, Pharmacy, Retail).
- `test_reports_database_down`: if the database cannot be reached, every report returns nothing instead of crashing.


## GitHub Link

https://github.com/nanditha1707/1103_Group04

## Disclaimer

This project is developed for educational purposes for INF1103 Programming Fundamentals.

The system is a proof-of-concept and should not be used as a replacement for professional medical advice, diagnosis, or treatment.