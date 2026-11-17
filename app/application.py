from collections.abc import Callable

from app.menu import MainMenu


class Application:

    def __init__(
        self, main_menu: MainMenu, on_exit: Callable[[], None]
    ) -> None:
        self.__main_menu = main_menu
        self.__on_exit = on_exit

    def run(self) -> None:
        """Run the main menu until the user exits. on_exit runs however
        the program stops, including Ctrl+C or an error."""
        try:
            while self.__main_menu.run_once():
                pass
        finally:
            self.__on_exit()
