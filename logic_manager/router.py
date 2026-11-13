from .classification import Classification
from .medicine_classifier import MedicineClassifier
from .route import Route

class Router:
    """
    Decides where a patient should go based off the AI output.
    Uses the MedicineClassifier that LogicManagerFactory passes in. It is
    None when the HSA data failed to load.
    """

    # Key the AI output contains when it failed validation.
    _ERROR_KEY = "error"

    # Keys where the medicines are stored in the AI output.
    _MEDICINE_KEYS = (
        "primary_diagnosis_medicine_1",
        "primary_diagnosis_medicine_2",
        "secondary_diagnosis_medicine_1",
        "secondary_diagnosis_medicine_2"
    )

    # Keys where the AI explains each diagnosis.
    _EXPLANATION_KEYS = (
        "primary_diagnosis_explanation",
        "secondary_diagnosis_explanation"
    )

    # Word the AI writes (in capitals) to flag an emergency.
    _EMERGENCY_KEYWORD = "EMERGENCY"

    # Where each classification sends the patient. 
    # Adding a new classification only needs a new entry here.
    _CLASSIFICATION_ROUTES = {
        Classification.GENERAL_SALE_LIST: Route.RETAIL,
        Classification.PHARMACY_ONLY: Route.PHARMACIST,
        Classification.PRESCRIPTION_ONLY: Route.DOCTOR
    }

    def __init__(
        self, classifier: MedicineClassifier | None
    ):
        self.__classifier = classifier

    def decide(self, ai_output: dict) -> Route | None:
        """
        Decide where the patient should go. Returns None if the AI
        output failed, so the patient is not routed.
        """

        # AI output failed validation, 
        # so the patient is not routed because the AI output is not reliable.
        if self._ERROR_KEY in ai_output:
            return None

        # AI flagged an emergency, this overrides every other route.
        if self._is_emergency(ai_output):
            return Route.EMERGENCY

        # Without HSA data the medicines cannot be checked, so see a doctor.
        if self.__classifier is None:
            return Route.DOCTOR

        # Classify every medicine the AI recommended.
        medicines = self._get_medicines(ai_output)
        classifications = []
        for medicine in medicines:
            classification = self.__classifier.classify(medicine)
            classifications.append(classification)

        # If a medicine is not in the HSA data, it cannot be confirmed as safe to buy at retail. 
        # or if there are no medicines recommended, send the patient to a doctor.
        # Currently does not occur but acts as a form of safeguarding for future code.
        has_unknown_medicine = None in classifications
        has_no_medicines = not classifications

        if has_unknown_medicine or has_no_medicines:
            return Route.DOCTOR

        # The strictest medicine decides the route. 
        # As the highest authority required should be the one to make the call.
        strictest = Classification.most_restrictive(classifications)
        return self._CLASSIFICATION_ROUTES[strictest]

    def _is_emergency(self, ai_output: dict) -> bool:
        """
        Return True if the AI wrote EMERGENCY in either diagnosis explanation. 
        Kept case-sensitive on purpose: the word in capitals is the AI's flag, 
        while a lower-case phrase like "no emergency signs" must not trigger it.
        """
        for key in self._EXPLANATION_KEYS:
            explanation = self._get_text(ai_output, key)
            if self._EMERGENCY_KEYWORD in explanation:
                return True
        return False

    def _get_medicines(self, ai_output: dict) -> list[str]:
        """
        Returns all the medicine's the AI recommended.
        """
        medicines = []
        for key in self._MEDICINE_KEYS:
            medicine = self._get_text(ai_output, key)
            if medicine:
                medicines.append(medicine)
        return medicines

    @staticmethod
    def _get_text(ai_output: dict, key: str) -> str:
        """
        Return the text stored under a key in the AI output, with spaces trimmed. 
        Missing, blank or non-text values become "".
        """
        value = ai_output.get(key)
        if isinstance(value, str):
            return value.strip()
        return ""
