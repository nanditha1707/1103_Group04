class EncryptionKeyError(Exception):
    """
    Raised when the program starts with an encryption key that is missing,
    malformed, not the key the database was encrypted with,
    or when the database cannot be reached to check the key.
    In these scenarios, main.py catches it, and stops the program.
    This ensures no patient record is ever saved or read with the wrong key, 
    or a missing key.
    """
