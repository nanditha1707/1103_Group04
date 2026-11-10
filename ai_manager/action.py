from enum import Enum


class Action(Enum):
    """What AiPipeline does after a failed attempt."""

    # Stop trying every model, e.g. the request is too large for any model.
    FAIL = "Fail immediately"
    # Try the same model again after a short wait, because the error is
    # likely transient.
    RETRY_SAME_MODEL = "Retry on the same model"
    # Move on to the next model in the list.
    SWITCH_MODEL = "Switch to the next model"
    # Skip the remaining models of the same provider, e.g. because its API
    # key is missing or invalid, which affects every one of its models.
    SWITCH_PROVIDER = "Switch immediately to the next model provider"
