import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    def __init__(self, password: str, salt: str | bytes):
        self.password = password.encode()
        self.salt = bytes.fromhex(salt) if isinstance(salt, str) else salt
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        self.key = self.kdf.derive(self.password)

    def encrypt(self, data: str) -> str:
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        encrypted_data = aesgcm.encrypt(nonce, data.encode(), None)
        return base64.b64encode(nonce + encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        encrypted_data_bytes = base64.b64decode(encrypted_data.encode())
        nonce = encrypted_data_bytes[:12]
        ciphertext = encrypted_data_bytes[12:]
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
