from dataclasses import dataclass


@dataclass(frozen=True)
class AIRequest:
    context: str
    prompt: str
    schema: dict
