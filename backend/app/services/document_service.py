"""Services for document management."""
import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Document, DocumentChunk, User
from app.schemas.schemas import DocumentCreate, DocumentUpdate
from app.rag.pipeline import RAGPipeline
from core.config import settings

class DocumentService:
    """Service for document operations."""

    def __init__(self, db: Session, rag_pipeline: RAGPipeline):
        self.db = db
        self.rag_pipeline = rag_pipeline

    def create_document(
        self,
        file_name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        current_user: User,
        document_create: DocumentCreate
    ) -> Document:
        """Create a new document."""
        # Create document record
        db_document = Document(
            title=document_create.title,
            description=document_create.description,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            size=file_size,
            uploaded_by_id=current_user.id
        )
        self.db.add(db_document)
        self.db.flush()  # Get the ID

        # Ingest into RAG pipeline
        try:
            self.rag_pipeline.ingest_document(
                file_path=file_path,
                file_type=file_type,
                document_id=db_document.id,
                metadata={
                    "title": document_create.title,
                    "file_name": file_name,
                    "uploaded_by": current_user.name,
                    "upload_date": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            # If RAG ingestion fails, delete the document record
            self.db.delete(db_document)
            self.db.commit()
            raise Exception(f"Failed to ingest document: {str(e)}")

        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_all_documents(self, skip: int = 0, limit: int = 100) -> tuple[List[Document], int]:
        """Get all documents with pagination."""
        query = self.db.query(Document).filter(Document.is_active == True)
        total = query.count()
        documents = query.offset(skip).limit(limit).all()
        return documents, total

    def get_user_documents(self, user_id: int, skip: int = 0, limit: int = 100) -> tuple[List[Document], int]:
        """Get documents uploaded by a specific user."""
        query = self.db.query(Document).filter(
            Document.uploaded_by_id == user_id,
            Document.is_active == True
        )
        total = query.count()
        documents = query.offset(skip).limit(limit).all()
        return documents, total

    def update_document(self, document_id: int, update_data: DocumentUpdate) -> Document:
        """Update a document."""
        document = self.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        if update_data.title:
            document.title = update_data.title
        if update_data.description is not None:
            document.description = update_data.description
        if update_data.is_active is not None:
            document.is_active = update_data.is_active

        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        """Delete a document."""
        document = self.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete from RAG pipeline
        try:
            self.rag_pipeline.delete_document(document_id)
        except Exception as e:
            print(f"Warning: Failed to delete from RAG pipeline: {str(e)}")

        # Delete file from storage
        if os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                print(f"Warning: Failed to delete file: {str(e)}")

        # Delete from database
        self.db.delete(document)
        self.db.commit()
        return True

    def search_documents(self, query: str, skip: int = 0, limit: int = 100) -> tuple[List[Document], int]:
        """Search documents by title or description."""
        search_query = self.db.query(Document).filter(
            Document.is_active == True
        ).filter(
            (Document.title.ilike(f"%{query}%")) |
            (Document.description.ilike(f"%{query}%"))
        )
        total = search_query.count()
        documents = search_query.offset(skip).limit(limit).all()
        return documents, total

    def get_document_statistics(self) -> Dict[str, Any]:
        """Get document management statistics."""
        total_documents = self.db.query(Document).filter(Document.is_active == True).count()
        total_size = sum(
            doc.size for doc in self.db.query(Document).filter(Document.is_active == True)
        ) or 0

        return {
            "total_documents": total_documents,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
