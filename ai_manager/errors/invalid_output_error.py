from ai_manager.action import Action
from .ai_manager_error import AIManagerError


class InvalidOutputError(AIManagerError):
    """Raised when the AI's reply is not valid JSON, or fails the ICD-11
    or HSA checks.

    Another try at the same model is likely to give a valid reply, so its
    action retries the same model.
    """

    action = Action.RETRY_SAME_MODEL
