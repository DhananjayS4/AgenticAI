import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class SecurityManager:
    def __init__(self, passphrase: str = "guardian-default-passphrase", salt_str: str = "guardian-salt-2026"):
        # Derive a 256-bit key from the passphrase and salt
        salt = salt_str.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=10000, # Lightweight iterations for quick local response
        )
        self.key = kdf.derive(passphrase.encode('utf-8'))
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string using AES-256-GCM and return base64 string."""
        if not plaintext:
            return ""
        # 12-byte initialization vector (nonce)
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        # Store nonce + ciphertext together
        combined = nonce + ciphertext
        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, ciphertext_b64: str) -> str:
        """Decrypt base64 ciphertext string using AES-256-GCM and return plaintext."""
        if not ciphertext_b64:
            return ""
        try:
            combined = base64.b64decode(ciphertext_b64)
            if len(combined) < 12:
                return "[Error: Ciphertext too short]"
            nonce = combined[:12]
            ciphertext = combined[12:]
            decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
            return decrypted.decode('utf-8')
        except Exception as e:
            return f"[Decryption Error: {str(e)}]"
