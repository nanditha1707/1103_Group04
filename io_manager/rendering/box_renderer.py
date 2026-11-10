from collections.abc import Sequence


class BoxRenderer:
    """
    This is used for drawing a box around text.

    Used for:
        - Main Menu
        - Healthcare Professional Portal menu
        - Query filter menu
        - Reports menu
        - Symptom menu
        - Confirmation menu (checking answers before submitting)
        - Patient results screen (queue number and diagnosis)

    Takes a list or tuple of lines and returns them as a single string
    with a box drawn around them. It can also be given a title (the
    header), which goes centred at the top. It only builds the text and
    does not print anything. The Console will print it.

    For e.g the main menu options:

        lines = ["1. Patient Registration",
                 "2. Healthcare Professional Portal",
                 "3. Exit"]
        render(lines, "Main Menu")

    returns this box:

        -------------------------------------
        |             Main Menu             |
        -------------------------------------
        | 1. Patient Registration           |
        | 2. Healthcare Professional Portal |
        | 3. Exit                           |
        -------------------------------------

    The report tables and patient query results use TableRenderer
    instead. This is because reports and query results are data and have 
    headers so a table with properly aligned headers has to be drawn.
    Menus are just lines of text, with no headings or columns to line up
    so they are generated differently.
    """

    # Space for "| " on the left and " |" on the right of each line.
    __PADDING = 4

    def __width(self, lines: Sequence[str], header: str | None = None) -> int:
        """
        Return the full box width: the longest line (or the header,
        if it is longer) plus the padding.
        """
        longest = max(len(line) for line in lines)
        if header:
            longest = max(longest, len(header))
        return longest + self.__PADDING

    def render(self, lines: Sequence[str], header: str | None = None) -> str:
        """
        Return the lines in a box, with an optional centered header.
        """
        box_width = self.__width(lines, header)
        separator = "-" * box_width
        rows = [separator]

        if header:
            rows.append("|" + header.center(box_width - 2) + "|")
            rows.append(separator)

        rows.extend("|" + f" {line}".ljust(box_width - 2) + "|" for line in lines)
        rows.append(separator)
        return "\n".join(rows)
