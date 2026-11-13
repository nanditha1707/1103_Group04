from io_manager import constants

from .choice_validator import ChoiceValidator


class YesNoValidator(ChoiceValidator):
    """
    Accepts only Y or N. One instance is shared by every Y/N
    question.
    """

    YES = "Y"
    NO = "N"

    def __init__(
        self
    ) -> None:
        super().__init__((self.YES, self.NO), constants.YES_NO_ERROR)
