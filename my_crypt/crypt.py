import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key_derivation(salt, master_password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt(key, value_to_encrypt):
    f = Fernet(key)
    encrypted_key = f.encrypt(value_to_encrypt)
    return encrypted_key


def decrypt(key, encrypted_key):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_key)
    except InvalidToken:
        return b''