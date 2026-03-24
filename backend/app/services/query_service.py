"""Services for query processing."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.database import Query, User
from app.rag.pipeline import RAGPipeline
from app.agents.orchestrator import AgentOrchestrator
import json


class QueryService:
    """Service for processing and managing queries."""

    def __init__(self, db: Session, rag_pipeline: RAGPipeline, agent_orchestrator: AgentOrchestrator):
        self.db = db
        self.rag_pipeline = rag_pipeline
        self.agent_orchestrator = agent_orchestrator

    async def process_query(
        self,
        query_text: str,
        user: User,
        document_filter: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the multi-agent system.
        
        Returns: {
            "answer": str,
            "sources": List[str],
            "confidence": float,
            "query_id": int
        }
        """
        # Process through agent orchestrator
        result = await self.agent_orchestrator.process_query(
            query=query_text,
            document_filter=document_filter,
            validate=True
        )

        # Store query in database
        db_query = Query(
            user_id=user.id,
            question=query_text,
            answer=result["answer"],
            source_documents=json.dumps(result.get("sources", [])),
            timestamp=datetime.utcnow()
        )
        self.db.add(db_query)
        self.db.commit()
        self.db.refresh(db_query)

        return {
            "query_id": db_query.id,
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.8),
            "validation_passed": result.get("validation_passed", True)
        }

    def get_user_queries(self, user_id: int, skip: int = 0, limit: int = 50):
        """Get user's query history."""
        return self.db.query(Query).filter(
            Query.user_id == user_id
        ).order_by(Query.timestamp.desc()).offset(skip).limit(limit).all()

    def get_query(self, query_id: int) -> Optional[Query]:
        """Get a specific query."""
        return self.db.query(Query).filter(Query.id == query_id).first()

    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query statistics."""
        total_queries = self.db.query(Query).count()
        
        # Most recent queries
        recent_queries = self.db.query(Query).order_by(
            Query.timestamp.desc()
        ).limit(10).all()

        return {
            "total_queries": total_queries,
            "recent_queries": [
                {
                    "id": q.id,
                    "question": q.question[:100],
                    "timestamp": q.timestamp.isoformat()
                }
                for q in recent_queries
            ]
        }
