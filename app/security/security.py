"""
Security utilities for TrueMesh Provider Intelligence
"""
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("security")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Centralized security management"""
    
    def __init__(self):
        self.settings = get_settings()
        self._cipher = None
    
    def get_cipher(self) -> Fernet:
        """Get or create Fernet cipher for encryption"""
        if self._cipher is None:
            # Ensure encryption key is properly formatted
            key = self.settings.encryption_key.encode()
            # If key is not 32 bytes, hash it to get consistent length
            if len(key) != 32:
                key = hashlib.sha256(key).digest()
            key_base64 = base64.urlsafe_b64encode(key)
            self._cipher = Fernet(key_base64)
        return self._cipher
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm
        )
        
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT access token"""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            cipher = self.get_cipher()
            encrypted = cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            cipher = self.get_cipher()
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def mask_pii(self, value: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Mask PII data (show only last N characters)"""
        if not value or len(value) <= visible_chars:
            return mask_char * len(value)
        
        masked_length = len(value) - visible_chars
        return (mask_char * masked_length) + value[-visible_chars:]
    
    def mask_email(self, email: str) -> str:
        """Mask email address"""
        if not email or "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + ("*" * (len(local) - 2)) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    def mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        # Remove non-digits for processing
        digits = ''.join(c for c in phone if c.isdigit())
        
        if len(digits) < 4:
            return "*" * len(phone)
        
        # Mask all but last 4 digits
        masked_digits = ("*" * (len(digits) - 4)) + digits[-4:]
        
        # Reconstruct with original formatting
        result = ""
        digit_idx = 0
        for char in phone:
            if char.isdigit():
                result += masked_digits[digit_idx]
                digit_idx += 1
            else:
                result += char
        
        return result
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    def hash_data(self, data: str) -> str:
        """Generate SHA-256 hash of data"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def sanitize_for_logging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for safe logging (mask sensitive fields)"""
        sensitive_fields = [
            "password", "secret", "token", "api_key",
            "email", "phone", "ssn", "credit_card"
        ]
        
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            if any(field in key_lower for field in sensitive_fields):
                if "email" in key_lower:
                    sanitized[key] = self.mask_email(str(value)) if value else None
                elif "phone" in key_lower:
                    sanitized[key] = self.mask_phone(str(value)) if value else None
                else:
                    sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get security manager singleton"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return get_security_manager().hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return get_security_manager().verify_password(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    return get_security_manager().create_access_token(data, expires_delta)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT access token"""
    return get_security_manager().decode_access_token(token)


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    return get_security_manager().encrypt_data(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return get_security_manager().decrypt_data(encrypted_data)


def mask_pii(value: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask PII data"""
    return get_security_manager().mask_pii(value, mask_char, visible_chars)


def mask_email(email: str) -> str:
    """Mask email address"""
    return get_security_manager().mask_email(email)


def mask_phone(phone: str) -> str:
    """Mask phone number"""
    return get_security_manager().mask_phone(phone)


def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize data for logging"""
    return get_security_manager().sanitize_for_logging(data)
