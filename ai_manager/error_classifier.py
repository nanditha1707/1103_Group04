from .action import Action
from .ai_provider import AIProvider
from .empty_reply_error import EmptyReplyError
from .missing_api_key_error import MissingApiKeyError


class ErrorClassifier:
    """Decides what AiPipeline does after a failed attempt.

    Errors that mean the same for every provider, a problem with the
    reply itself, are handled here. Errors from an API are passed to the
    provider that raised them. This class never imports an SDK, so a new
    provider needs no change here.
    """

    def classify(self, error: Exception, provider: AIProvider) -> Action:
        """Return the Action to take after the provider's attempt raised
        the error."""
        if isinstance(error, MissingApiKeyError):
            return Action.SWITCH_PROVIDER

        # The model answered with no text, e.g. it refused or a safety
        # filter blocked it. The same prompt sent to the same model is
        # likely to fail the same way, so retrying would waste time.
        if isinstance(error, EmptyReplyError):
            return Action.SWITCH_MODEL

        # The reply was not valid JSON (json.JSONDecodeError) or failed the
        # ICD-11 / HSA checks. Both are ValueErrors and likely to pass on
        # another try, so retry the same model. Any other ValueError is
        # treated the same way.
        if isinstance(error, ValueError):
            return Action.RETRY_SAME_MODEL

        action = provider.classify_error(error)

        # An error the provider does not recognise is unexpected, so stop.
        if action is None:
            return Action.FAIL

        return action
