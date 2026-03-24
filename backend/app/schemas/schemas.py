"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    STUDENT = "student"


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str


class UserCreate(UserBase):
    """User creation schema."""
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if v is not None and len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        return v


class User(UserBase):
    """User schema."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    description: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    pass


class DocumentUpdate(BaseModel):
    """Document update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Document(DocumentBase):
    """Document schema."""
    id: int
    file_name: str
    file_type: str
    size: int
    uploaded_by: User
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Document list response."""
    documents: List[Document]
    total: int


# Query Schemas
class QueryRequest(BaseModel):
    """Query request schema."""
    question: str = Field(..., min_length=1, max_length=2000)
    relevant_documents: Optional[List[int]] = None  # Optional document filter


class QueryResponse(BaseModel):
    """Query response schema."""
    id: int
    question: str
    answer: str
    source_documents: Optional[List[dict]] = None
    timestamp: datetime
    confidence_score: Optional[float] = None


class ConversationMessage(BaseModel):
    """Conversation message schema."""
    role: str  # "user" or "assistant"
    content: str


# Health Check
class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    version: str
