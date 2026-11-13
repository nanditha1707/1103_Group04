from app.menu import MainMenu


class Application:

    def __init__(
        self, main_menu: MainMenu
    ) -> None:
        self.__main_menu = main_menu

    def run(self) -> None:
        while self.__main_menu.run_once():
            pass
