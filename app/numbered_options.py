from collections.abc import Sequence

from .menu_option import MenuOption


class NumberedOptions[T: MenuOption]:

    def __init__(
        self, options: Sequence[T]
    ) -> None:
        self.__options = list(options)

    def __len__(self) -> int:
        return len(self.__options)

    def lines(self) -> list[str]:
        return [f"{number}. {option.label}" for number, option in enumerate(self.__options, start=1)]

    def get(self, choice: str) -> T:
        return self.__options[int(choice) - 1]
