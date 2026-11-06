from abc import ABC, abstractmethod

class Console(ABC):
    """Interface for input and output. 
    Ensures that there is no need for a direct input or print call in the other classes.
    Every other IO class receives a Console instead of calling input()
    """

    @abstractmethod
    def ask(self, prompt: str) -> str:
        """Show the prompt and return the raw text the user entered.
        Works akin to a normal input() call, but with a few differences. The prompt is
        shown to the user, but the text returned is not stripped or uppercased.
        The callers are responsible for any normalization they want to do on the text.
        """

    @abstractmethod
    def show(self, text: str) -> None:
        """Show a block of text to the user.
        This is the only way to show text to the user. 
        It works akin to a normal print() call.
        """