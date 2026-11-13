from typing import override

from app import constants
from app.interfaces import RegistrationScreens
from app.triage_pipeline import TriagePipeline

from .menu_action import MenuAction


class RegistrationAction(MenuAction):

    def __init__(
        self, screens: RegistrationScreens, triage_pipeline: TriagePipeline
    ) -> None:
        super().__init__(constants.REGISTRATION_LABEL)
        self.__screens = screens
        self.__triage_pipeline = triage_pipeline

    @override
    def run(self) -> bool:
        # 1. I/O manager: collect the patient's answers
        # Runs the questions and the confirmation screen. The IO manager
        # shows the confirmed or exit message itself, and returns None
        # if registration did not finish.
        answers = self.__screens.collect_registration()
        if answers is not None:
            self.__triage_pipeline.process(answers)
        return True
