# from passlib import pwd
# from passlib.context import CryptContext
from argon2 import PasswordHasher

# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


pwd_context = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(hashed_password, plain_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# def generate_password() -> str:
#     return pwd.genword()
