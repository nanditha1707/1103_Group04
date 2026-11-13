from .ai_request import AIRequest


class PromptBuilder:
    """Builds the AIRequest for a patient from their filtered answers.

    The system context and JSON schema are the same for every patient, so
    they are given once, in the constructor.
    """

    def __init__(self, context: str, schema: dict):
        # System prompt sent with every request.
        self.__context = context
        # JSON schema the reply must follow.
        self.__schema = schema

    def build(self, answers_filtered: dict) -> AIRequest:
        """Return the request for the already filtered answers, with one
        "- key: value" line per answer."""
        prompt = "Presenting patient answers:\n"

        for key, value in answers_filtered.items():
            prompt += f"- {key}: {value}\n"

        return AIRequest(self.__context, prompt, self.__schema)
