from app.interfaces import UserPrompt

class StartupFailure:
    """
    Runs when the program cannot start safely. 
    Running it shows the reason through the IO manager and stops the program.
    """
    def __init__(
        self, prompt: UserPrompt, message: str
    ) -> None:
        self.__prompt = prompt
        self.__message = message

    def run(self) -> None:
        self.__prompt.show_message(self.__message)
        raise SystemExit(1)
