from abc import abstractmethod

from app.menu_option import MenuOption


class PortalAction(MenuOption):

    @abstractmethod
    def run(self) -> str | None:
        pass
