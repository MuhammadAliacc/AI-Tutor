"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import UserCreate, UserLogin, User, Token
from app.services.user_service import UserService
from app.core.security import decode_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=User)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (student)."""
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login a user and return access token."""
    user_service = UserService(db)
    user = user_service.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = user_service.create_access_token(user)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800
    )


def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token."""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_service = UserService(db)
    user = user_service.get_user_by_id(int(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


# Dependency to get current user from header
from fastapi import Header

async def get_current_user_from_header(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Extract and validate user from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    return get_current_user(token, db)
