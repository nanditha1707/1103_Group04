from .ai_request import AIRequest


class PromptBuilder:
    def __init__(self, context: str, schema: dict):
        self.__context = context
        self.__schema = schema

    def build(self, answers_filtered: dict) -> AIRequest:
        prompt = "Presenting patient answers:\n"

        for key, value in answers_filtered.items():
            prompt += f"- {key}: {value}\n"

        return AIRequest(self.__context, prompt, self.__schema)
