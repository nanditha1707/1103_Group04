import textwrap
from collections.abc import Mapping

from io_manager import constants


class ResultView:
    """
    Builds the final message telling the patient what to do next.

    It only builds the lines of text. The code that draws and shows them
    is in separate classes. BoxRenderer draws the box around the lines
    and Console shows it, both called from IOManager.show_result(). 

    Only the method build_lines() is public since it is used by
    IOManager class. The other methods are private since they are used
    within build_lines() itself and do not need to be accessed from the
    outside.
    """

    # Long messages are wrapped to this width so the result box does not
    # get too wide.
    WRAP_WIDTH = 70

    def build_lines(
        self, ai_output: Mapping[str, object], logic_result: Mapping[str, str | None]
    ) -> list[str]:
        """
        Return the result lines. Missing fields are skipped instead
        of shown as None. Used by IOManager.show_result() which draws
        the lines in a box.

        Example: result from logic manager is {"route": "Doctor", "queue_number":
        "D008"}. Returns:

            [
                "Your Queue Number: D008",
                "",
                "Please take a seat and wait for your queue number to be called to see",
                "a doctor.",
            ]

        Example 2: result from logic manager is {"route": "Retail",
        "queue_number": "P013"}. Retail patients go to the pharmacy.
        Returns:

            [
                "Your Queue Number: PR013",
                "",
                "Please proceed to the pharmacy and wait for your queue number to be",
                "called.",
            ]

        ai_output is no longer used, since Retail patients no longer see
        their diagnoses and medicines. It is kept so that
        IOManager.show_result() does not need to change.
        """
        # Read the route and queue number decided by logic_manager.
        route = logic_result.get("route")
        queue_number = logic_result.get("queue_number")
        lines: list[str] = []

        # First add the queue number, followed by a blank line.
        if queue_number:
            queue_line = constants.QUEUE_NUMBER_LINE.format(queue_number=queue_number)
            lines.append(queue_line)
            lines.append("")

        # Then add what the patient should do next for their route.
        route_message = constants.ROUTE_MESSAGES[route]
        lines.extend(self.__wrap(route_message))

        return lines

    def __wrap(self, text: str) -> list[str]:
        """
        Split text into lines no wider than the wrap width. Used for
        the route message so the result box does not get too wide.
        """
        # textwrap.wrap only breaks lines between words.
        return textwrap.wrap(text, self.WRAP_WIDTH)
