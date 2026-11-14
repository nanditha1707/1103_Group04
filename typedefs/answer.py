# Type alias for the answer type, meant for all the registration answers.
# It can be a string, a list of strings,
# or None if the question does not apply to the patient.
type Answer = str | list[str] | None
