from .action import Action
from .ai_manager_error import AIManagerError
from .ai_provider import AIProvider


class ErrorClassifier:
    """Decides what ModelFallback does after a failed attempt.

    ai_manager's own errors, such as a missing API key or a problem with
    the reply itself, are AIManagerError subclasses that carry their own
    action. Errors from an API are passed to the provider that raised
    them. This class never imports an SDK, so a new provider needs no
    change here.
    """

    def classify(self, error: Exception, provider: AIProvider) -> Action:
        """Return the Action to take after the provider's attempt raised
        the error."""
        # One of ai_manager's own errors, e.g. an empty reply switches
        # model and an invalid reply retries the same model.
        if isinstance(error, AIManagerError):
            return error.action

        action = provider.classify_error(error)

        # An error the provider does not recognise is unexpected, so stop.
        if action is None:
            return Action.FAIL

        return action
