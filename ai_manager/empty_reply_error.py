from .action import Action
from .ai_manager_error import AIManagerError


class EmptyReplyError(AIManagerError):
    """Raised by a provider when the model returns no usable text, e.g. it
    refused, a safety filter blocked the reply, or the reply was cut off.

    The same prompt sent to the same model is likely to fail the same
    way, so its action switches model instead of retrying. This replaces
    checking a ValueError for an exact message string.
    """

    action = Action.SWITCH_MODEL
