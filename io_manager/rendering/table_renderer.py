from collections.abc import Mapping

import pandas as pd


class TableRenderer:
    """
    This is used for drawing data as a grid table.

    Used for:
        - Patient query results (current and past patient information)
        - Specific Medicine Count report
        - Medicine Breakdown report
        - Patient Type Breakdown report

    Takes a DataFrame or a dict and returns it as a single string drawn
    as a grid table:
        - DataFrame: patient query results, since they are rows picked
          from patient records. Each row of the DataFrame becomes a row 
          of the table.
        - dict: medical reports, since they are counts (for e.g
          {"Doctor": 1, "Pharmacy": 1}). A dict becomes one row: the
          keys are the column headings and the values go in the cells.
    
    It only builds the text and does not print anything. The Console 
    will print it. The grid itself is drawn by the tabulate library, through
    DataFrame.to_markdown.

    For e.g the Medicine Breakdown report:

        report = {"PARACETAMOL": 2, "IBUPROFEN": 2, "NAPROXEN": 1}
        render(report, "Medicine Breakdown Report")

    returns this table:

        +------------------------------------------+
        |        Medicine Breakdown Report         |
        +---------------+-------------+------------+
        |   PARACETAMOL |   IBUPROFEN |   NAPROXEN |
        +===============+=============+============+
        |             2 |           2 |          1 |
        +---------------+-------------+------------+
    """

    # Widest a column may get before its text wraps. Must match the 10
    # that data_manager.print_or_export assumes for each column.
    MAX_COLUMN_WIDTH = 10

    def render(
        self, report: pd.DataFrame | Mapping[str, object], title: str = ""
    ) -> str:
        """
        Return the report as a grid table, with the title on top if
        one is given.
        """

        # to_markdown only exists on DataFrames, so a dict is converted
        # to a df
        if isinstance(report, pd.DataFrame):
            report_df = report
        else:
            report_df = pd.DataFrame([report])

        grid_table = report_df.to_markdown(
            index=False,
            tablefmt="grid",
            floatfmt=".2f",
            maxcolwidths=self.MAX_COLUMN_WIDTH,
        )

        # If no title then don't need to build title box
        if not title:
            return grid_table

        # Build title box
        # Every line of a grid table is the same length, so the first
        # line gives the full width. The title box has a "|" each side.
        grid_width = len(grid_table.splitlines()[0])
        inner_width = grid_width - 2
        title_border = "+" + "-" * inner_width + "+"
        title_row = "|" + title.center(inner_width) + "|"

        # The table's own top border closes the title box.
        return "\n".join([title_border, title_row, grid_table])
