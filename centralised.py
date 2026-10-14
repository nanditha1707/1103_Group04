import subprocess
import sys


def run_tests():
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