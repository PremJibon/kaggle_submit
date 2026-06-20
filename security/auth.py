from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
import logging
import secrets

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User model."""
    id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.now()


class AuthService:
    """Authentication service for user management."""

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.users: Dict[str, User] = {}

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        user_id = f"user_{secrets.token_urlsafe(8)}"
        hashed_password = self.get_password_hash(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {username}")
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        for user in self.users.values():
            if user.username == username and self.verify_password(password, user.hashed_password):
                return user
        return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token."""
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return self.users.get(user_id)

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)

    def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key."""
        # In a real implementation, this would check against a database
        return len(api_key) > 0