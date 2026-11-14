import subprocess
import sys
from typing import NoReturn


def run_tests() -> NoReturn:
    """Run every test in the tests folder with pytest, then exit with
    pytest's return code so a failed test also fails this script."""
    # sys.executable runs pytest with the same Python as this script,
    # so the installed packages match.
    # -q prints a shorter summary, -s shows print output from the tests.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "-s"
        ],
        check=False
    )

    sys.exit(result.returncode)


if __name__ == "__main__":
    run_tests()
