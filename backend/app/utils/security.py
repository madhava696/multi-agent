from passlib.context import CryptContext

password_context = CryptContext(schemes=["pbkdf2_sha256"])

def hash_password(password:str)->str:
    return password_context.hash(password)

def verify_password(password:str,hashed_password:str)->str:
    return password_context.verify(password,hashed_password)

