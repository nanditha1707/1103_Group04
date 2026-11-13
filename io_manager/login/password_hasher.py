import bcrypt 

class PasswordHasher:
    """Hashes passwords and verifies login attempts using bcrypt."""
    def hash(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("Password cannot be empty.")
        hashed_bytes = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        return hashed_bytes.decode("utf-8")
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False   