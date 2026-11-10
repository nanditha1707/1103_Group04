from io_manager import messages
from io_manager.form.registration_form import RegistrationForm
from io_manager.questions import SymptomQuestion, TextQuestion
from io_manager.rendering import BoxRenderer
from io_manager.rules import (
    ChainStopRule, ConsentRequiredRule, EmergencyAnswerRule, MinimumAgeRule, SkipIfAnswerEquals,
    StopRule
)
from io_manager.symptoms import (
    CatalogueSymptomAction, FeverSymptomAction, PresetSymptomAction, SymptomCatalogue, SymptomMenu,
    YesNoPrompt
)
from io_manager.validators import (
    ChoiceValidator, NonNegativeIntegerValidator, PhoneNumberValidator, RegexValidator,
    YesNoValidator
)


class RegistrationFactory:
    """
    Defines the parameters that affects how the registration parameters run,
    such as the questions asked, the order, validators,
    and what the break conditions for the registration process are.

    If a clinic's registration requirements change, in terms of questions, 
    this is the only class that will have to be edited.
    Unless some sort of new validation rule is required, 
    in which a new validator class/subclass will have to be made.
    In the current setup, we have made this to serve as a default for registration.
    If any other clinics have differing setups, a subclass of this class can simply be made,
    where it will override any methods that differ, such as build_form and/or build_stop_rule.
    """

    # Maximum age for a patient to be considered real. 
    MAXIMUM_AGE = 120
    MAXIMUM_ONSET_DAYS = 365
    # Patients under this age cannot self register. 
    # This is clinic policy, separate from the age validator's range of 0 to MAXIMUM_AGE,
    # which only rejects ages that cannot be real.
    MINIMUM_SELF_REGISTRATION_AGE = 18
    # Regex pattern to ensure a name starts with a letter,
    # and may only contain letters, spaces, hyphens and apostrophes.
    NAME_PATTERN = r"[A-Z][A-Z' \-]*"
    # Regex pattern to ensure NRIC/FIN is valid. 
    # The first letter must be one of S, T, F, G or M, followed by 7 digits and a final letter. 
    # E.G. S1234567D
    NRIC_PATTERN = r"[STFGM][0-9]{7}[A-Z]"
    # List of keys for questions that require immediate attention and stop registration,
    # if the user replies Y.
    EMERGENCY_KEYS = (
        "chest_pain",
        "breathing_difficulties",
        "signs_of_stroke",
        "self_harm",
    )

    def build_form(
        self, catalogue: SymptomCatalogue, renderer: BoxRenderer
    ) -> RegistrationForm:
        """
        Build the clinic's registration questions, in order.
        Currently there exists 16 questions.
        """
        # Creates the Y/N Validator, used by all Y/N questions, 
        # and the symptom follow-up prompts.
        yes_no = YesNoValidator()
        # Used for questions that require follow up in the form of Y/N,
        # such as fever and difflib.
        yes_no_prompt = YesNoPrompt(yes_no)

        # Constructs the Symptom Menu for use as a local variable.
        symptom_menu = SymptomMenu(
            [
                PresetSymptomAction(messages.COUGH_LABEL, "COUGH"),
                PresetSymptomAction(messages.FLU_LABEL, "FLU"),
                PresetSymptomAction(messages.HEADACHE_LABEL, "HEADACHE"),
                FeverSymptomAction(yes_no_prompt),
                CatalogueSymptomAction(catalogue, yes_no_prompt),
            ],
            renderer,
        )
        # Create the rule for skipping based off gender
        skip_if_male = SkipIfAnswerEquals("gender", "M")

        # Consreucts the form accordingly with its prompts and validators. 
        # For the values that are meant to be used in the ai manager later, 
        # the share_with_ai boolean flag iss et to true here.
        return RegistrationForm([
            TextQuestion(
                "consent",
                messages.CONSENT_PROMPT, 
                yes_no
            ),
            TextQuestion(
                "name",
                messages.NAME_PROMPT,
                RegexValidator(self.NAME_PATTERN, messages.NAME_ERROR),
            ),
            TextQuestion(
                "nric",
                messages.NRIC_PROMPT,
                RegexValidator(self.NRIC_PATTERN, messages.NRIC_ERROR),
            ),
            TextQuestion(
                "gender",
                messages.GENDER_PROMPT,
                ChoiceValidator(("M", "F"), messages.GENDER_ERROR),
                share_with_ai=True,
            ),
            TextQuestion(
                "age",
                messages.AGE_PROMPT,
                # 0 is a real age (an infant registered by a parent), so it
                # is accepted here and the minimum age rule sends them to
                # manual registration.
                NonNegativeIntegerValidator(
                    minimum=0,
                    maximum=self.MAXIMUM_AGE,
                    error=messages.AGE_ERROR.format(maximum=self.MAXIMUM_AGE),
                ),
                share_with_ai=True,
            ),
            TextQuestion("phone_number", messages.PHONE_PROMPT, PhoneNumberValidator()),
            TextQuestion(
                "pregnancy",
                messages.PREGNANCY_PROMPT,
                yes_no,
                share_with_ai=True,
                skip_rule=skip_if_male,
            ),
            TextQuestion(
                "chest_pain", messages.CHEST_PAIN_PROMPT, yes_no,
                share_with_ai=True,
            ),
            TextQuestion(
                "breathing_difficulties", messages.BREATHING_PROMPT, yes_no,
                share_with_ai=True,
            ),
            TextQuestion(
                "signs_of_stroke", messages.STROKE_PROMPT, yes_no,
                share_with_ai=True,
            ),
            TextQuestion(
                "self_harm", messages.SELF_HARM_PROMPT, yes_no,
                share_with_ai=True,
            ),
            SymptomQuestion(
                "current_symptoms", messages.SYMPTOMS_PROMPT, symptom_menu,
                share_with_ai=True,
            ),
            TextQuestion(
                "symptom_onset_days",
                messages.ONSET_PROMPT,
                NonNegativeIntegerValidator(
                    minimum=0,
                    maximum=self.MAXIMUM_ONSET_DAYS,
                    error=messages.ONSET_DAYS_ERROR.format(
                        maximum=self.MAXIMUM_ONSET_DAYS
                    ),
                ),
                share_with_ai=True,
            ),
            TextQuestion(
                "chronic_conditions", messages.CHRONIC_PROMPT, yes_no,
                share_with_ai=True,
            ),
            TextQuestion(
                "current_medications", messages.MEDICATIONS_PROMPT, yes_no,
                share_with_ai=True,
            ),
            TextQuestion(
                "drug_allergies", messages.ALLERGIES_PROMPT, yes_no,
                share_with_ai=True,
            ),
        ])

    def build_stop_rule(self) -> StopRule:
        """
        Build the chain of rules that determine whether registration should stop, 
        to be utilised in both the registration questionnaire and the confirmation screen.
        The order is followed, meaning if multiple conditions are somehow broken at once, 
        the first messgae will still win. 
        Currently, this is impossible.
        """
        return ChainStopRule([
            ConsentRequiredRule("consent"),
            EmergencyAnswerRule(self.EMERGENCY_KEYS),
            MinimumAgeRule("age", self.MINIMUM_SELF_REGISTRATION_AGE),
        ])
