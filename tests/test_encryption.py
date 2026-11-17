import sys
from pathlib import Path

import pandas as pd
import pytest
from cryptography.fernet import Fernet

sys.path.append(str(Path(__file__).resolve().parent.parent))

from data_manager import constants
from data_manager.security import FernetCipher, RecordEncryptor


class TestEncryption:
    # ==========================================================
    # TEST 1 - ENCRYPT AND DECRYPT WITH FERNET
    # ==========================================================

    def test_fernet_round_trip(self):
        """
        Check that FernetCipher turns text into ciphertext and back again,
        and that a different key cannot read it.

        Steps:
        1. Make two ciphers each with its own random key so the test does
           not need the key from the .env file.
        2. Encrypt "S1234567A" with the first cipher.
        3. Decrypt the result with the same cipher.
        4. Try to decrypt the same result with the second cipher.

        Example:
            cipher.encrypt("S1234567A")
                -> "gAAAAABn3x...Qw=="  (different every run)
            cipher.decrypt("gAAAAABn3x...Qw==")
                -> "S1234567A"
            other_cipher.decrypt("gAAAAABn3x...Qw==")
                -> raises ValueError

        Expected:
        - The ciphertext is not the plain NRIC.
        - Decrypting with the same key gives back "S1234567A".
        - Decrypting with a different key raises ValueError. This is the
          error KeyVerifier relies on to detect a wrong key at the startup.
        """

        cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        other_cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))

        ciphertext = cipher.encrypt("S1234567A")
        decrypted = cipher.decrypt(ciphertext)

        print("\nSCENARIO: Encrypt And Decrypt With Fernet")
        print("Expected: ciphertext differs from S1234567A, decrypts back to it")
        print("Expected: a different key raises ValueError")
        print("Actual:", ciphertext[:20], "... ->", decrypted)

        assert ciphertext != "S1234567A"
        assert decrypted == "S1234567A"

        with pytest.raises(ValueError):
            other_cipher.decrypt(ciphertext)

    # ==========================================================
    # TEST 2 - ENCRYPT ONLY SENSITIVE COLUMNS
    # ==========================================================

    def test_record_encryptor_sensitive_columns(self):
        """
        Check that RecordEncryptor encrypts only the columns listed in
        ENCRYPTED_COLUMNS and that decrypt_table restores them.

        Steps:
        1. Make a FernetCipher with a random key and wrap it in a
           RecordEncryptor that uses the real ENCRYPTED_COLUMNS list.
        2. Encrypt a record with one plain column (queue_number), two
           sensitive columns (name,nric) and one missing value (drug_allergies).
        3. Put the encrypted record into a one-row DataFrame, the same
           shape a database query returns, and decrypt it.

        Example:
            record:
                {"queue_number": "D001", "name": "Alex Tan",
                 "nric": "S1234567A", "drug_allergies": None}
            encrypt_record(record):
                {"queue_number": "D001", "name": "gAAAAABn...",
                 "nric": "gAAAAABn...", "drug_allergies": None}
            decrypt_table(DataFrame([encrypted])):
                queue_number  name      nric       drug_allergies
                D001          Alex Tan  S1234567A  None

        Expected:
        - queue_number is not in ENCRYPTED_COLUMNS so it stays "D001".
        - name and nric are replaced with ciphertext.
        - drug_allergies stays None so the database saves it as NULL.
        - The original record is not changed because encrypt_record works
          on a copy.
        - decrypt_table gives back "Alex Tan" and "S1234567A".
        """

        cipher = FernetCipher(Fernet.generate_key().decode("utf-8"))
        encryptor = RecordEncryptor(cipher, constants.ENCRYPTED_COLUMNS)

        record = {
            "queue_number": "D001",
            "name": "Alex Tan",
            "nric": "S1234567A",
            "drug_allergies": None
        }

        encrypted = encryptor.encrypt_record(record)
        decrypted = encryptor.decrypt_table(pd.DataFrame([encrypted]))

        print("\nSCENARIO: Encrypt Only Sensitive Columns")
        print("Expected: queue_number unchanged, name and nric encrypted")
        print("Expected: missing drug_allergies stays None")
        print("Expected: decrypt_table restores the original values")
        print("Actual:", encrypted)

        assert encrypted["queue_number"] == "D001"
        assert encrypted["name"] != "Alex Tan"
        assert encrypted["nric"] != "S1234567A"
        assert encrypted["drug_allergies"] is None
        assert record["name"] == "Alex Tan"

        assert decrypted.iloc[0]["name"] == "Alex Tan"
        assert decrypted.iloc[0]["nric"] == "S1234567A"
        assert decrypted.iloc[0]["queue_number"] == "D001"
