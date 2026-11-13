from dataclasses import dataclass


@dataclass(frozen=True) #Read-only so user details cannot be altered after login
class User:
    nric: str
    password_hash: str
    role: str