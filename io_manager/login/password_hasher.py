import bcrypt 

class PasswordHasher:
    def hash(self, plain_password: str) -> str:
        if not plain_password:
            raise ValueError("Password cannot be empty.")
        hashed_bytes = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        return hashed_bytes.decode("utf-8")