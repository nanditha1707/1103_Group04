from collections.abc import Sequence


class BoxRenderer:
    """Takes a list of lines (for e.g lines = ["1. Register", "2. Exit"])
    and returns them as a single string with a box drawn around them. 
    It can also be given a title (the header), which goes centred at 
    the top. It only builds the text and does not print anything. The 
    Console will print it.
    """

    # Space for "| " on the left and " |" on the right of each line.
    __PADDING = 4

    def __width(self, lines: Sequence[str], header: str | None = None) -> int:
        """Return the full box width: the longest line (or the header,
        if it is longer) plus the padding."""
        longest = max(len(line) for line in lines)
        if header:
            longest = max(longest, len(header))
        return longest + self.__PADDING

    def render(self, lines: Sequence[str], header: str | None = None) -> str:
        """Return the lines in a box, with an optional centered header."""
        box_width = self.__width(lines, header)
        separator = "-" * box_width
        rows = [separator]

        if header:
            rows.append("|" + header.center(box_width - 2) + "|")
            rows.append(separator)

        rows.extend("|" + f" {line}".ljust(box_width - 2) + "|" for line in lines)
        rows.append(separator)
        return "\n".join(rows)
