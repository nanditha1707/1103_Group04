from dataclasses import dataclass


@dataclass(frozen=True)
class AIRequest:
    """One request to send to a model.

    Every model gets the same request, so it is built once by
    PromptBuilder and handed to each provider. It is frozen dataclass 
    so no provider can change it for the next one.
    """

    context: str
    prompt: str
    schema: dict
