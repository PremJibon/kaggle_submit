from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
import logging
import secrets
import hashlib

logger = logging.getLogger(__name__)


class User(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.now()


class AuthService:

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.users: Dict[str, User] = {}

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.get_password_hash(plain_password) == hashed_password

    def get_password_hash(self, password: str) -> str:
        salt = "knowledge_assistant_salt"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def create_user(self, username: str, email: str, password: str) -> User:
        user_id = f"user_{secrets.token_urlsafe(8)}"
        hashed_password = self.get_password_hash(password)
        user = User(id=user_id, username=username, email=email, hashed_password=hashed_password)
        self.users[user_id] = user
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username and self.verify_password(password, user.hashed_password):
                return user
        return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    def get_current_user(self, token: str) -> Optional[User]:
        payload = self.verify_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        return self.users.get(user_id) if user_id else None