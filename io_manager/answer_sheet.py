# Type alias for the answer type, meant for all the registration answers. 
# It can be a string, a list of strings, 
# or None if the question does not apply to the patient.
type Answer = str | list[str] | None


class AnswerSheet:
    """
    Holds the patient's answers,in a private dict. 
    The dict is hidden so answers can only change through record_answer and mark_not_applicable.
    """

    def __init__(self) -> None:
        self.__answers: dict[str, Answer] = {}
    
    def get_answer(self, key: str) -> Answer:
        # Return the stored answer, or None if there is none.
        return self.__answers.get(key)

    def record_answer(self, key: str, value: Answer) -> None:
        # Store an answer under its question key.
        self.__answers[key] = value

    def mark_not_applicable(self, key: str) -> None:
        # Sets the answer to None to indicate that the question does not apply to this patient.
        # Only used for pregnancy.
        self.record_answer(key, None)

    def to_dict(self) -> dict[str, Answer]:
        # Return all the answers as a dict, 
        # for use in the other managers.
        return dict(self.__answers)


