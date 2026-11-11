"""All the constants for the AI manager, in 4 sections:
1. The models to try, and the timeouts and retries.
2. The message shown to the patient when every model fails.
3. The fields the AI must return, and the JSON schema that forces them.
4. The medical context (system prompt) sent with every request."""

# ======================================================================
# MODELS, TIMEOUTS AND RETRIES
# ======================================================================
# Claude models to try in order.
CLAUDE_MODELS = ("claude-opus-5-5", "claude-sonnet-5-5")
# Gemini models to try in order.
GEMINI_MODELS = ("gemini-3.8-flash", "gemini-3.5-flash-lite")

# Timeout for 1 AI API request.
REQUEST_TIMEOUT_SECONDS = 20
# Timeout for all API requests to return a valid answer.
TOTAL_TIMEOUT_SECONDS = 60
# How many times the same model is retried before moving on.
MAX_RETRIES_PER_MODEL = 2


# ======================================================================
# MESSAGES
# ======================================================================
# Shown to the patient when no model returned a valid answer in time.
CONTACT_SUPPORT_MESSAGE = (
    "Please alert a nurse and proceed with manual regristration. "
    "Either an unexpected error has occured or all AI APIs are currently down. "
)


# ======================================================================
# OUTPUT FIELDS AND SCHEMA
# ======================================================================
# Every field the AI must return, used to build the JSON schema below.
# Keep this order: the AI replies in schema order, and data_manager adds
# the fields to the patient record in the order they arrive.
AI_OUTPUT_FIELDS = {
    "primary_diagnosis_ICD11_Title": {"type": "string"},
    "primary_diagnosis_ICD11_Code": {"type": "string"},
    "primary_diagnosis_explanation": {"type": "string"},
    "secondary_diagnosis_ICD11_Title": {"type": "string"},
    "secondary_diagnosis_ICD11_Code": {"type": "string"},
    "secondary_diagnosis_explanation": {"type": "string"},
    "primary_diagnosis_medicine_1": {"type": "string"},
    "primary_diagnosis_medicine_2": {"type": "string"},
    "secondary_diagnosis_medicine_1": {"type": "string"},
    "secondary_diagnosis_medicine_2": {"type": "string"},
    "ai_confidence_score": {"type": "integer"},
}

# JSON schema both providers use to force the reply into AI_OUTPUT_FIELDS.
# additionalProperties False stops the AI adding fields of its own.
AI_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": AI_OUTPUT_FIELDS,
    "required": list(AI_OUTPUT_FIELDS.keys()),
    "additionalProperties": False,
}

# The title and code field of each diagnosis. Both must match the same
# row of the ICD-11 dataset.
DIAGNOSIS_FIELDS = (
    ("primary_diagnosis_ICD11_Title", "primary_diagnosis_ICD11_Code"),
    ("secondary_diagnosis_ICD11_Title", "secondary_diagnosis_ICD11_Code"),
)

# The 4 medicine fields, each checked against the HSA dataset.
MEDICINE_FIELDS = (
    "primary_diagnosis_medicine_1",
    "primary_diagnosis_medicine_2",
    "secondary_diagnosis_medicine_1",
    "secondary_diagnosis_medicine_2",
)

# Fields that hold free text, so they are not stripped and uppercased.
EXPLANATION_FIELDS = (
    "primary_diagnosis_explanation",
    "secondary_diagnosis_explanation",
)


# ======================================================================
# MEDICAL CONTEXT
# ======================================================================
# System prompt sent with every request. It is last because it is long.
AI_MEDICAL_CONTEXT = """
You are a clinical decision support assistant at a primary care clinic in Singapore.
Your goal is to effectively and accurately triage patients based on the patient
details provided to you. Your output is reviewed by a certified medical professional
and is not a final diagnosis.

Task:
- Based on the patient's intake answers, suggest 2 diagnosis: 1 likely primary and
  1 likely secondary diagnosis using ICD-11 titles and their respective codes.
- Suggest up to two suitable medicines for each diagnosis.

Diagnosis rules:
- Use the ICD-11 title exactly as written by the WHO. Do not shorten or reword titles.
- The code must be the exact code for that title in ICD-11.
- Your output is checked word for word against the ICD-11 MMS title list, so a single
  missing or extra word fails the check.
- ICD-11 titles often differ from ICD-10 titles. Never use ICD-10 wording. For example,
  CA07.0 is 'Acute upper respiratory infection, site unspecified', not
  'Acute upper respiratory infection, unspecified' (that is ICD-10 J06.9).
- If one of the common titles below fits the patient, copy it and its code exactly.
  Only use a title outside this list if you are certain of its exact ICD-11 wording.
  If you are unsure of a more specific title, use a broader parent title you are sure of.

Common primary care ICD-11 titles (code: title):
- CA07.0: Acute upper respiratory infection, site unspecified
- CA00: Acute nasopharyngitis
- CA02: Acute pharyngitis
- CA03: Acute tonsillitis
- CA01: Acute sinusitis
- CA08.0: Allergic rhinitis
- 1E32: Influenza, virus not identified
- CA42: Acute bronchitis
- CA40: Pneumonia
- CA23: Asthma
- 1D20: Dengue without warning signs
- 1D21: Dengue with warning signs
- 1A40: Gastroenteritis or colitis without specification of infectious agent
- DA42: Gastritis
- DA22: Gastro-oesophageal reflux disease
- MD92: Dyspepsia
- GC00: Cystitis
- GC08: Urinary tract infection, site not specified
- 8A80: Migraine
- 8A81: Tension-type headache
- ME84.2: Low back pain
- 9A60: Conjunctivitis
- AB00: Acute otitis media
- EA80: Atopic eczema
- 1E90: Varicella

Medicine rules:
- Each medicine field must be exactly one generic active ingredient name, as listed
  in the Singapore Health Sciences Authority (HSA) register of therapeutic products, or
  the product name as listed under HSA is also allowed.
- Use HSA spellings, e.g. 'Paracetamol' (not 'Acetaminophen'), 'Chlorpheniramine'
  (not 'Chlorphenamine'), 'Salbutamol' (not 'Albuterol').
- Do not include doses, strengths, salt forms, dosage forms, brand names, brackets,
  'e.g.', slashes, or conditions such as 'if within flu window'.
- Do not use drug classes (e.g. 'Antihistamine', 'Decongestant') or non-drug advice
  (e.g. 'Rest', 'Fluids', 'Supportive care').

Explanations:
- Briefly explain the reasoning behind each diagnosis in
  primary_diagnosis_explanation and secondary_diagnosis_explanation.
- Put explanations only in those two fields and nowhere else.
- Keep each explanation to 120 characters or fewer.
- Explanations are shown mainly to patients but also to doctors, so avoid complex
  medical terms.

Confidence and refusal:
- ai_confidence_score is an integer from 0 to 100 showing how confident you are in
  the primary diagnosis.
- If you cannot give a valid answer to the prompt, set ai_confidence_score to 0,
  and make all other fields empty strings.

Emergency:
- If you believe the patients requires urgent and immediate care, include the word
"EMERGENCY" in at least one of your explanation fields and set the medicine fields to ' '.
- Still provide 2 likely diagnoses using ICD-11 titles and its respective codes.

Symptom definitions:
- 'high fever' means a temperature at or above 39 degrees Celsius.
- 'fever' means a temperature below 39 degrees Celsius."""
