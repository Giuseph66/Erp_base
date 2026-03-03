"""
Encryption Module for Data Protection
"""
import os
import base64
import hashlib
import secrets
from typing import Optional, Tuple, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption service.
        
        Args:
            key: Encryption key (will generate if not provided)
        """
        self.key = key or self._generate_key()
        self.fernet = Fernet(self.key)
    
    def _generate_key(self) -> bytes:
        """Generate a new Fernet key."""
        return Fernet.generate_key()
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.fernet.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted string
        """
        try:
            decoded = base64.b64decode(encrypted_data)
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: Optional[bytes] = None,
        iterations: int = 100000
    ) -> Tuple[bytes, bytes]:
        """
        Derive an encryption key from a password.
        
        Args:
            password: User password
            salt: Optional salt (generated if not provided)
            iterations: PBKDF2 iterations
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """
        Hash a password securely.
        
        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt) as hex strings
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        return pwd_hash.hex(), salt.hex()
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """
        Verify a password against stored hash.
        
        Args:
            password: Plain text password to verify
            stored_hash: Stored hash (hex string)
            salt: Salt used for hashing (hex string)
            
        Returns:
            True if password matches, False otherwise
        """
        salt_bytes = bytes.fromhex(salt)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000
        )
        
        return secrets.compare_digest(pwd_hash.hex(), stored_hash)


class AsymmetricEncryption:
    """RSA asymmetric encryption for secure key exchange."""
    
    def __init__(self, key_size: int = 2048):
        """
        Initialize with new or existing key pair.
        
        Args:
            key_size: RSA key size in bits
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def get_public_key_pem(self) -> bytes:
        """Get public key in PEM format."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def get_private_key_pem(self, password: Optional[str] = None) -> bytes:
        """Get private key in PEM format."""
        encryption_algorithm = serialization.BestAvailableEncryption(
            password.encode()
        ) if password else serialization.NoEncryption()
        
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
    
    def encrypt_with_public_key(self, data: bytes, public_key_pem: bytes) -> bytes:
        """
        Encrypt data using a public key.
        
        Args:
            data: Data to encrypt
            public_key_pem: Public key in PEM format
            
        Returns:
            Encrypted data
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted
    
    def decrypt_with_private_key(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using private key.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        decrypted = self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Token length in bytes
        
    Returns:
        Hex-encoded secure token
    """
    return secrets.token_hex(length)


def secure_compare(a: str, b: str) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal, False otherwise
    """
    return secrets.compare_digest(a.encode(), b.encode())
