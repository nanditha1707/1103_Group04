from ai_manager.errors import InvalidOutputError
from . import constants
from .model_fallback import ModelFallback
from .output_validator import OutputValidator
from .prompt_builder import PromptBuilder
from .reply_parser import ReplyParser


class AIManager:
    """The class main.py uses to get a diagnosis from the AI.

    It is given the objects that do the work through its constructor:
    - PromptBuilder turns the patient's answers into a request.
    - ModelFallback sends the request to each model. If there are errors
      it handles it accordingly.
    - ReplyParser and OutputValidator turn a reply into a checked output.

    It does not create any of them, so it does not depend on any provider.
    AIManagerFactory builds the one main.py uses, with the Claude and
    Gemini models in constants.py. Tests can build one directly e.g. with
    a ModelFallback of fake providers.
    """

    def __init__(
        self, prompt_builder: PromptBuilder, parser: ReplyParser, validator: OutputValidator, fallback: ModelFallback
    ):
        self.__prompt_builder = prompt_builder
        self.__parser = parser
        self.__validator = validator
        self.__fallback = fallback

    def get_ai_output(self, answers_filtered: dict) -> dict:
        """Return the validated AI output for the filtered patient answers.

        Returns {"error": message} if the ICD-11 dataset did not load, or
        if no model gave a valid answer before the total timeout.
        """
        # Without ICD data the diagnoses cannot be checked so the AI is not
        # called and the patient is sent to manual registration.
        if not self.__validator.has_icd_data:
            return {"error": constants.CONTACT_SUPPORT_MESSAGE}

        request = self.__prompt_builder.build(answers_filtered)
        output = self.__fallback.run(request, self.__read_reply)

        if output is None:
            return {"error": constants.CONTACT_SUPPORT_MESSAGE}

        return output

    def __read_reply(self, reply: str) -> dict:
        """Parse and check one reply, and return it as the output.

        Raises InvalidOutputError if it is not valid JSON or fails the
        ICD-11 / HSA checks, so ModelFallback retries the same model.
        """
        output = self.__parser.parse(reply)

        if not self.__validator.is_valid(output):
            raise InvalidOutputError(
                "AI output not found in the ICD11 / HSA datasets"
            )

        return output
