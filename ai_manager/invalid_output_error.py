class InvalidOutputError(Exception):
    """Raised when the AI's reply is not valid JSON, or fails the ICD-11
    or HSA checks.

    Another try at the same model is likely to give a valid reply, so
    ErrorClassifier retries the same model.
    """
