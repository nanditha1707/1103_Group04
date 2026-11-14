class QuitRequested(Exception):
    """
    Raised when the user types quit in the middle of a portal lookup.
    HealthcarePortal catches it and goes back to the main menu.
    """
    pass
