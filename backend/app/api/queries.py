"""Query/Chat API routes."""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query as QueryParam
from sqlalchemy.orm import Session
from typing import Optional, List
import asyncio
import json
from app.core.database import get_db
from app.api.auth import get_current_user_from_header
from app.models.database import User
from app.schemas.schemas import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.rag.pipeline import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/queries", tags=["Queries"])


# Simple in-memory connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


@router.post("/ask", response_model=QueryResponse)
async def ask_query(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Ask a question to the AI Tutor.
    
    The system will retrieve relevant documents, contextualize them,
    generate an answer, and validate it through multiple agents.
    """
    try:
        query_service = QueryService(
            db,
            RAGPipeline(),
            AgentOrchestrator(RAGPipeline())
        )
        
        result = await query_service.process_query(
            query_text=query_request.question,
            user=current_user,
            document_filter=query_request.relevant_documents
        )
        
        return QueryResponse(
            id=result["query_id"],
            question=query_request.question,
            answer=result["answer"],
            source_documents=[
                {"name": source, "type": "document"}
                for source in result["sources"]
            ],
            confidence_score=result["confidence"],
            timestamp=query_service.get_query(result["query_id"]).timestamp
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: str = QueryParam(None),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat functionality.
    
    Clients should pass the JWT token as a query parameter.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    from app.api.auth import get_current_user
    try:
        current_user = get_current_user(token, db)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "query":
                query_text = message.get("question", "")
                document_filter = message.get("document_filter")
                
                try:
                    query_service = QueryService(
                        db,
                        RAGPipeline(),
                        AgentOrchestrator(RAGPipeline())
                    )
                    
                    # Send processing status
                    await websocket.send_json({
                        "type": "status",
                        "message": "Processing your question...",
                        "stage": "processing"
                    })
                    
                    result = await query_service.process_query(
                        query_text=query_text,
                        user=current_user,
                        document_filter=document_filter
                    )
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "query_id": result["query_id"],
                        "question": query_text,
                        "answer": result["answer"],
                        "sources": result["sources"],
                        "confidence": result["confidence"],
                        "validation_passed": result["validation_passed"]
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/history")
def get_query_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Get current user's query history."""
    query_service = QueryService(db, RAGPipeline(), AgentOrchestrator(RAGPipeline()))
    queries = query_service.get_user_queries(current_user.id, skip, limit)
    
    return {
        "queries": [
            {
                "id": q.id,
                "question": q.question,
                "timestamp": q.timestamp.isoformat(),
                "sources_count": len(json.loads(q.source_documents or "[]"))
            }
            for q in queries
        ],
        "total": db.query(db.models.Query).filter(db.models.Query.user_id == current_user.id).count()
    }


@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """Get a specific query by ID."""
    query_service = QueryService(db, RAGPipeline(), AgentOrchestrator(RAGPipeline()))
    query = query_service.get_query(query_id)
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check ownership
    if query.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this query"
        )
    
    return QueryResponse(
        id=query.id,
        question=query.question,
        answer=query.answer,
        source_documents=json.loads(query.source_documents or "[]"),
        timestamp=query.timestamp
    )
