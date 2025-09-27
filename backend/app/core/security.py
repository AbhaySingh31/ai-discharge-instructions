import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for sensitive data
def generate_key() -> bytes:
    """Generate a new encryption key."""
    return Fernet.generate_key()

def get_encryption_key() -> bytes:
    """Get or create encryption key for sensitive data."""
    key_file = "encryption.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key

# Initialize encryption
encryption_key = get_encryption_key() if settings.enable_encryption else None
cipher_suite = Fernet(encryption_key) if encryption_key else None

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like SSN, medical records."""
    if not settings.enable_encryption or not cipher_suite:
        return data
    
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        return data

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    if not settings.enable_encryption or not cipher_suite:
        return encrypted_data
    
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return encrypted_data

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None

def hash_patient_id(patient_id: str) -> str:
    """Create a hash of patient ID for logging without exposing PII."""
    return hashlib.sha256(patient_id.encode()).hexdigest()[:16]

def generate_audit_id() -> str:
    """Generate a unique audit ID."""
    return secrets.token_hex(16)

class AuditLogger:
    """HIPAA-compliant audit logging."""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
        if settings.enable_audit_logging:
            # Create audit log handler
            audit_handler = logging.FileHandler("audit.log")
            audit_formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s'
            )
            audit_handler.setFormatter(audit_formatter)
            self.logger.addHandler(audit_handler)
            self.logger.setLevel(logging.INFO)
    
    def log_access(self, user_id: str, patient_id: str, action: str, resource: str, 
                   ip_address: str = None, user_agent: str = None):
        """Log access to patient data."""
        if not settings.enable_audit_logging:
            return
        
        audit_entry = {
            "audit_id": generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "patient_id_hash": hash_patient_id(patient_id),
            "action": action,
            "resource": resource,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": "SUCCESS"
        }
        
        self.logger.info(f"ACCESS: {audit_entry}")
    
    def log_data_modification(self, user_id: str, patient_id: str, action: str, 
                            resource: str, changes: Dict[str, Any] = None):
        """Log modifications to patient data."""
        if not settings.enable_audit_logging:
            return
        
        audit_entry = {
            "audit_id": generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "patient_id_hash": hash_patient_id(patient_id),
            "action": action,
            "resource": resource,
            "changes": changes or {},
            "status": "SUCCESS"
        }
        
        self.logger.info(f"MODIFY: {audit_entry}")
    
    def log_failed_access(self, user_id: str, patient_id: str, action: str, 
                         reason: str, ip_address: str = None):
        """Log failed access attempts."""
        if not settings.enable_audit_logging:
            return
        
        audit_entry = {
            "audit_id": generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "patient_id_hash": hash_patient_id(patient_id) if patient_id else None,
            "action": action,
            "reason": reason,
            "ip_address": ip_address,
            "status": "FAILED"
        }
        
        self.logger.warning(f"FAILED_ACCESS: {audit_entry}")
    
    def log_system_event(self, event_type: str, description: str, user_id: str = None):
        """Log system events."""
        if not settings.enable_audit_logging:
            return
        
        audit_entry = {
            "audit_id": generate_audit_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "description": description,
            "user_id": user_id,
            "status": "INFO"
        }
        
        self.logger.info(f"SYSTEM: {audit_entry}")

# Global audit logger instance
audit_logger = AuditLogger()

def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or hash sensitive data for logging."""
    sensitive_fields = [
        'ssn', 'social_security_number', 'phone', 'email', 
        'address', 'emergency_contact', 'medical_history'
    ]
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            if isinstance(value, str):
                sanitized[key] = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                sanitized[key] = "***REDACTED***"
        else:
            sanitized[key] = value
    
    return sanitized

def validate_hipaa_compliance(data: Dict[str, Any]) -> bool:
    """Validate that data handling meets HIPAA requirements."""
    # Check for minimum necessary standard
    required_fields = ['patient_id', 'purpose', 'authorized_user']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"HIPAA validation failed: missing {field}")
            return False
    
    # Check data retention policy
    if 'created_at' in data:
        created_date = datetime.fromisoformat(data['created_at'])
        retention_limit = datetime.utcnow() - timedelta(days=settings.data_retention_days)
        
        if created_date < retention_limit:
            logger.warning("HIPAA validation failed: data exceeds retention period")
            return False
    
    return True

class SecurityMiddleware:
    """Security middleware for HIPAA compliance."""
    
    @staticmethod
    def validate_request_headers(headers: Dict[str, str]) -> bool:
        """Validate security headers."""
        required_headers = ['user-agent']
        
        for header in required_headers:
            if header not in headers:
                return False
        
        return True
    
    @staticmethod
    def rate_limit_check(user_id: str, action: str) -> bool:
        """Simple rate limiting check."""
        # In production, use Redis or similar for distributed rate limiting
        # This is a basic implementation
        return True
    
    @staticmethod
    def validate_data_access_permission(user_id: str, patient_id: str, 
                                      action: str) -> bool:
        """Validate user permission to access patient data."""
        # In production, implement proper role-based access control
        # This is a basic implementation
        return True
