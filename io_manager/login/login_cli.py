from getpass import getpass
from auth_service import AuthService
from user import User


def prompt_login(auth_service: AuthService, max_attempts: int = 3) -> User | None:
    """Prompt for NRIC and password in the terminal until login succeeds or attempts run out."""
    for attempt in range(1, max_attempts + 1):
        nric = input("Enter NRIC: ")
        password = getpass("Enter Password: ")

        user = auth_service.authenticate(nric, password)
        if user is not None:
            print(f"Login successful. Welcome ({user.role})!")
            return user

        remaining = max_attempts - attempt
        if remaining > 0:
            print(f"Invalid NRIC or password. {remaining} attempt(s) left.\n")

    print("Too many failed attempts. Exiting.")
    return None