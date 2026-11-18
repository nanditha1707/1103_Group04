from typing import Protocol


class Labelled(Protocol):
    """
    Anything that can be shown as one line of a numbered menu.

    It is kept in typedefs so io_manager, which draws the menus, and app,
    which builds the options, share one definition without importing each
    other. It is a Protocol, so any object with a matching label property
    fits, e.g. MenuOption and SymptomMenuAction.
    """

    @property
    def label(self) -> str:
        """
        Return the text shown next to the option's number in the menu,
        e.g. "Patient Registration" for the line "1. Patient Registration".
        """
