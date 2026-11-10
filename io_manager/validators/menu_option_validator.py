from io_manager import messages
from io_manager.validators.chain_validator import ChainValidator
from io_manager.validators.non_negative_integer_validator import NonNegativeIntegerValidator
from io_manager.validators.not_empty_validator import NotEmptyValidator


class MenuOptionValidator(ChainValidator):
    """
    Subclass of chain validator meant for checking menu option inputs.
    It first checks if the input is blank, followed by if its a valid input,
    within the bounds of the minium and maximum value set.
    """

    def __init__(
        self,
        *,
        maximum: int | None = None,
        blank_error: str = messages.EMPTY_INPUT_ERROR,
        error: str = messages.POSITIVE_WHOLE_NUMBER_ERROR,
    ) -> None:
        super().__init__([
            NotEmptyValidator(blank_error),
            NonNegativeIntegerValidator(minimum=1, maximum=maximum, error=error),
        ])