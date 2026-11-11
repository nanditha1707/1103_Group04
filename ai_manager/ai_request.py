from dataclasses import dataclass


@dataclass(frozen=True)
class AIRequest:
    """One request to send to a model: the system context, the patient
    prompt and the JSON schema the reply must follow.

    Every model gets the same request, so it is built once by
    PromptBuilder and handed to each provider in turn. It is frozen so no
    provider can change it for the next one.
    """

    context: str
    prompt: str
    schema: dict
