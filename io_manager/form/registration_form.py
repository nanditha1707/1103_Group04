from collections.abc import Mapping, Sequence

from io_manager.patient_answers import Answer, PatientAnswers
from io_manager.questions.question import Question


class RegistrationForm:
    """
    Class that holds the ordered questions,
    and the methods to navigate through them,
    skipping questions that do not apply.
    It also saves each answer through apply_answer,
    so questions that no longer apply are always cleared.

    The questions themselves are constructed outside this class, 
    and passed in during initialisation. 
    The questions parsed in are determined by RegistrationFactory,
    which means adding or removing questions does not require changing this class, only the factory.
    """

    # Sequences is used for type hint as the question order matters.
    def __init__(
        self, questions: Sequence[Question]
    ) -> None:
        self.__questions = tuple(questions)

    @property
    def questions(self) -> tuple[Question, ...]:
        return self.__questions

    def next_index(self, index: int, answers: PatientAnswers) -> int:
        """
        Return the index of the next question that applies, passing
        over skipped questions.

        The only question that can be skipped right now is pregnancy, 
        which is skipped if the patient is male.
        """
        index += 1
        while (
            index < len(self.__questions)
            and self.__questions[index].should_skip(answers)
        ):
            index += 1
        return index

    def previous_index(self, index: int, answers: PatientAnswers) -> int:
        """
        Return the index of the last question the patient answered before this one, 
        passing over skipped questions. 
        """
        previous = index - 1
        while previous > 0 and self.__questions[previous].should_skip(answers):
            previous -= 1
        return previous

    def apply_answer(self, answers: PatientAnswers, key: str, value: Answer) -> None:
        """
        Store an answer then clear every question that no longer applies.

        The two steps always happen together so they are kept in one method.
        e.g. changing gender from F to M must also clear the pregnancy answer,
        otherwise a stored pregnancy answer of Y would still be sent to the AI.
        The screens call this instead of PatientAnswers.record_answer directly.
        """
        answers.record_answer(key, value)
        self.__mark_skipped(answers)

    def __mark_skipped(self, answers: PatientAnswers) -> None:
        # Mark every question that does not apply as not applicable.
        # Private, so it only ever runs as part of apply_answer.
        for question in self.__questions:
            if question.should_skip(answers):
                answers.mark_not_applicable(question.key)

    def first_unanswered(self, answers: PatientAnswers) -> Question | None:
        """
        Return the first question that applies to the patient but has no answer,
        only applicable to pregnancy question after gender change currently.

        Only used in confirmation screen.
        """
        for question in self.__questions:
            if (
                # Checks if the question should be skipped.
                not question.should_skip(answers)
                # Checks if the question has no answer.
                and answers.get_answer(question.key) is None
            ):
                # Returns the question that should be answered but isnt.
                return question
        return None

    # Mapping[str, Answer] is used here instead of PatientAnswers,
    # to make it clear that this method is read-only and does not change the answers in any way.
    def filter_for_ai(self, answers: Mapping[str, Answer]) -> dict[str, Answer]:
        """
        Return only the answers marked share_with_ai.
        This ensures personal information is never sent to the AI. 
        Takes the finished answers as a mapping input since it only needs to be read.

        The lines are just essentially for loops shortened for cleanliness of code.
        If expanded for clarity, the shared questions would become a filtering for loop,
        while the return statement would become a for loop,
        that checks if the question is in the shared questions list, 
        and if so, adds it to the return dictionary.
        """
        # Essentially appends any questions that are marked share_with_ai,
        # to the shared_questions list, which is then used to filter the answers mapping.
        shared_questions = [q for q in self.__questions if q.share_with_ai]
        # .get keeps every shared key, 
        # with None for a question that has no answer (pregnancy).
        return {q.key: answers.get(q.key) for q in shared_questions}