from ai_manager.action import Action


class AIManagerError(Exception):
    """Base class for the errors ai_manager raises itself, as opposed to
    the errors an AI provider's SDK raises.

    Each subclass sets action to what ModelFallback does after that error,
    so ErrorClassifier reads it from the error instead of checking each
    error type in turn. A new error of this kind is a new subclass with
    its own action, with no change to ErrorClassifier.
    """

    # What ModelFallback does after this error. Each subclass overrides it.
    # If no subclass overrides it then it is an unexpected error and 
    # action should be to fail immediately.
    action: Action = Action.FAIL
