"""Admin API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user_from_header
from app.models.database import User, UserRole
from app.services.document_service import DocumentService
from app.services.user_service import UserService
from app.services.query_service import QueryService
from app.rag.pipeline import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user_from_header)):
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/dashboard/stats")
def get_dashboard_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for admin."""
    document_service = DocumentService(db, RAGPipeline())
    user_service = UserService(db)
    query_service = QueryService(db, RAGPipeline(), AgentOrchestrator(RAGPipeline()))
    
    doc_stats = document_service.get_document_statistics()
    query_stats = query_service.get_query_statistics()
    
    return {
        "documents": doc_stats,
        "queries": query_stats,
        "users": {
            "total": user_service.get_user_count()
        },
        "system": {
            "version": "1.0.0",
            "status": "operational"
        }
    }


@router.get("/users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users."""
    user_service = UserService(db)
    users = user_service.get_all_users(skip, limit)
    
    return {
        "users": users,
        "total": user_service.get_user_count()
    }


@router.get("/documents/stats")
def get_document_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get document statistics."""
    document_service = DocumentService(db, RAGPipeline())
    return document_service.get_document_statistics()


@router.get("/queries/stats")
def get_query_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get query statistics."""
    query_service = QueryService(db, RAGPipeline(), AgentOrchestrator(RAGPipeline()))
    return query_service.get_query_statistics()
