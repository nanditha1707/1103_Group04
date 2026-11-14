from collections.abc import Iterable

from io_manager.console import Console, TerminalConsole
from io_manager.form import RegistrationFactory
from io_manager.rendering import BoxRenderer, TableRenderer
from io_manager.screens import ConfirmationScreen, Questionnaire, ResultView
from io_manager.symptoms import SymptomCatalogue
from io_manager.validators import DateValidator

from .manager import IOManager


class IOManagerFactory:
    """
    Builds the IOManager that ApplicationFactory uses.

    This is the only class that creates IOManager's parts, such as the renderers,
    the screens and the date validator. IOManager is given every object it needs instead
    so each one can be swapped or faked without changing IOManager.

    The questions and stop rules come from a RegistrationFactory. A different clinic setup
    is a RegistrationFactory subclass passed in here, and a different front end such as a GUI
    is a Console subclass passed in here.
    """

    @staticmethod
    def create(
        symptom_terms: Iterable[str], registration_factory: RegistrationFactory, console: Console | None = None
    ) -> IOManager:
        """
        Return an IOManager whose symptom menu offers the given symptom terms
        and whose questions come from registration_factory.

        console defaults to a TerminalConsole.
        """
        if console is None:
            console = TerminalConsole()

        box_renderer = BoxRenderer()
        form = registration_factory.build_form(SymptomCatalogue(symptom_terms), box_renderer)
        # Shared by both screens, so they always stop for the same reasons.
        stop_rule = registration_factory.build_stop_rule()

        return IOManager(
            console,
            form,
            Questionnaire(console, form, stop_rule),
            ConfirmationScreen(console, form, stop_rule, box_renderer),
            ResultView(),
            box_renderer,
            TableRenderer(),
            DateValidator()
        )
