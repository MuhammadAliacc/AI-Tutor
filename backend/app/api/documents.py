"""Document API routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from app.core.database import get_db
from app.api.auth import get_current_user_from_header
from app.models.database import User, UserRole
from app.schemas.schemas import Document, DocumentListResponse, DocumentCreate, DocumentUpdate
from app.services.document_service import DocumentService
from app.rag.pipeline import RAGPipeline
from core.config import settings

router = APIRouter(prefix="/api/documents", tags=["Documents"])


def require_admin(current_user: User = Depends(get_current_user_from_header)):
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = "",
    description: str = "",
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Upload a new document (Admin only)."""
    # Validate file
    if not title:
        title = file.filename
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Save file
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document
    try:
        document_service = DocumentService(db, RAGPipeline())
        document_create = DocumentCreate(
            title=title,
            description=description
        )
        
        document = document_service.create_document(
            file_name=file.filename,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            current_user=admin_user,
            document_create=document_create
        )
        
        return document
    except Exception as e:
        # Clean up file if document creation failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """List all documents."""
    document_service = DocumentService(db, RAGPipeline())
    documents, total = document_service.get_all_documents(skip, limit)
    return DocumentListResponse(documents=documents, total=total)


@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Get a specific document."""
    document_service = DocumentService(db, RAGPipeline())
    document = document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.put("/{document_id}", response_model=Document)
def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a document (Admin only)."""
    document_service = DocumentService(db, RAGPipeline())
    try:
        document = document_service.update_document(document_id, update_data)
        return document
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a document (Admin only)."""
    document_service = DocumentService(db, RAGPipeline())
    try:
        document_service.delete_document(document_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/search/query")
def search_documents(
    q: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Search documents by title or description."""
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query is required"
        )
    
    document_service = DocumentService(db, RAGPipeline())
    documents, total = document_service.search_documents(q, skip, limit)
    return DocumentListResponse(documents=documents, total=total)
