from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
import os

logger = logging.getLogger(__name__)


class EncryptionService:
    """Encryption service for data protection."""

    def __init__(self, password: str = None):
        if password:
            self.key = self._derive_key(password)
        else:
            self.key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.key)

    def _derive_key(self, password: str) -> bytes:
        """Derive an encryption key from a password."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt_data(self, data: str) -> str:
        """Encrypt a string."""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt a dictionary."""
        import json
        json_data = json.dumps(data)
        return self.encrypt_data(json_data)

    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt a dictionary."""
        import json
        decrypted = self.decrypt_data(encrypted_data)
        return json.loads(decrypted)

    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """Encrypt a file."""
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.cipher_suite.encrypt(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            
            logger.info(f"Encrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return False

    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """Decrypt a file."""
        try:
            with open(input_path, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self.cipher_suite.decrypt(encrypted)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            
            logger.info(f"Decrypted file: {input_path} -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return False

    def generate_key(self) -> str:
        """Generate a new encryption key."""
        return Fernet.generate_key().decode()