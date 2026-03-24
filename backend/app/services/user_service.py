"""Services for user management."""
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.database import User, UserRole
from app.schemas.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from core.config import settings

class UserService:
    """Service for user operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate, role: UserRole = UserRole.STUDENT) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise ValueError(f"User with email {user_create.email} already exists")

        # Create new user
        db_user = User(
            email=user_create.email,
            name=user_create.name,
            hashed_password=get_password_hash(user_create.password),
            role=role,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    def create_access_token(self, user: User) -> str:
        """Create access token for a user."""
        data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(data, expires)

    def update_user(self, user_id: int, update_data: UserUpdate) -> User:
        """Update a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        if update_data.name:
            user.name = update_data.name
        if update_data.email:
            # Check if new email is already in use
            existing = self.db.query(User).filter(
                User.email == update_data.email,
                User.id != user_id
            ).first()
            if existing:
                raise ValueError(f"Email {update_data.email} is already in use")
            user.email = update_data.email
        if update_data.password:
            user.hashed_password = get_password_hash(update_data.password)

        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100):
        """Get all users."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_user_count(self) -> int:
        """Get total user count."""
        return self.db.query(User).count()
