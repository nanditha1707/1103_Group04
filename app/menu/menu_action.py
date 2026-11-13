from abc import abstractmethod

from app.menu_option import MenuOption


class MenuAction(MenuOption):

    @abstractmethod
    def run(self) -> bool:
        pass
