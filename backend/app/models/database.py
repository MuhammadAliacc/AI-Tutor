"""Data models for database."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="uploaded_by")
    queries = relationship("Query", back_populates="user")


class Document(Base):
    """Document model for uploaded learning materials."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)
    file_name = Column(String)
    file_type = Column(String)  # pdf, docx, txt, md
    size = Column(Integer)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploaded_by = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


# class DocumentChunk(Base):
#     """Document chunks for RAG."""
#     __tablename__ = "document_chunks"

#     id = Column(Integer, primary_key=True, index=True)
#     document_id = Column(Integer, ForeignKey("documents.id"))
#     chunk_index = Column(Integer)
#     content = Column(Text)
#     metadata = Column(Text, nullable=True)  # JSON string
#     created_at = Column(DateTime, default=datetime.utcnow)

#     document = relationship("Document", back_populates="chunks")

class DocumentChunk(Base):
    """Document chunks for RAG."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    chunk_metadata = Column(Text, nullable=True)  # renamed from 'metadata'
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

class Query(Base):
    """User queries for auditing and analytics."""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text)
    answer = Column(Text)
    source_documents = Column(Text, nullable=True)  # JSON string with document IDs
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="queries")
