import sys
from pathlib import Path

from cryptography.fernet import Fernet

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import constants
from data_manager.security import FernetCipher, KeyVerifier
from fakes import FakeKeyCheckStore


class TestKeyVerifier:
    # ==========================================================
    # TEST 1 - CORRECT KEY PASSES THE STARTUP CHECK
    # ==========================================================

    def test_correct_key_passes(self):
        """
        Check that KeyVerifier accepts the key the database was encrypted with.

        Steps:
        1. Make a FernetCipher with a random key.
        2. Encrypt KEY_CHECK_TEXT with it, the same way the check value
           is saved in the database.
        3. Run verify with the same cipher.

        Expected:
        - verify returns None, meaning the key is correct.
        """

        cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        check_value = cipher.encrypt(constants.KEY_CHECK_TEXT)
        verifier = KeyVerifier(cipher, FakeKeyCheckStore((check_value,)), constants.KEY_CHECK_TEXT)

        result = verifier.verify()

        print("\nSCENARIO: Correct Key Passes The Startup Check")
        print("Expected: None")
        print("Actual:", result)

        assert result is None

    # ==========================================================
    # TEST 2 - WRONG KEY FAILS THE STARTUP CHECK
    # ==========================================================

    def test_wrong_key_fails(self):
        """
        Check that KeyVerifier rejects a key that is different from the one
        the database was encrypted with.

        Steps:
        1. Make two FernetCiphers, each with its own random key.
        2. Encrypt KEY_CHECK_TEXT with the first cipher, as if the
           database was set up with that key.
        3. Run verify with the second cipher, as if the .env file had
           a different key.

        Expected:
        - verify returns the message saying the key does not match.
        """

        database_cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        env_cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        check_value = database_cipher.encrypt(constants.KEY_CHECK_TEXT)
        verifier = KeyVerifier(env_cipher, FakeKeyCheckStore((check_value,)), constants.KEY_CHECK_TEXT)

        result = verifier.verify()

        print("\nSCENARIO: Wrong Key Fails The Startup Check")
        print("Expected: a message saying the key does not match")
        print("Actual:", result)

        assert result is not None
        assert "does not match" in result

    # ==========================================================
    # TEST 3 - NOTHING TO CHECK THE KEY AGAINST
    # ==========================================================

    def test_no_check_value_to_verify(self):
        """
        Check that KeyVerifier reports a clear message when it cannot get
        a check value from the database.

        Steps:
        1. Run verify with a store that returns None, as if the database
           could not be reached.
        2. Run verify with a store that returns an empty list, as if the
           database has no check value saved.

        Expected:
        - The first returns the message saying the database could not be reached.
        - The second returns the message saying there is no check value.
        """

        cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        unreachable = KeyVerifier(cipher, FakeKeyCheckStore(None), constants.KEY_CHECK_TEXT)
        empty = KeyVerifier(cipher, FakeKeyCheckStore(()), constants.KEY_CHECK_TEXT)

        unreachable_result = unreachable.verify()
        empty_result = empty.verify()

        print("\nSCENARIO: Nothing To Check The Key Against")
        print("Expected: 'could not be reached' and 'no encryption check value'")
        print("Actual:", unreachable_result, "|", empty_result)

        assert unreachable_result is not None
        assert "could not be reached" in unreachable_result
        assert empty_result is not None
        assert "no encryption check value" in empty_result
