"""Multi-agent AI orchestration system."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOpenAI

# Prompt class location changed across langchain versions
try:
    from langchain.prompts import ChatPromptTemplate
except ModuleNotFoundError:
    try:
        from langchain_community.prompts import ChatPromptTemplate
    except ModuleNotFoundError:
        from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain.output_parsers import PydanticOutputParser
except ModuleNotFoundError:
    try:
        from langchain_core.output_parsers import PydanticOutputParser
    except ModuleNotFoundError:
        # Fallback in case environment has older/custom langchain_community layout
        from langchain_community.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from core.config import settings
from app.rag.pipeline import RAGPipeline
import json


class AgentMessage(BaseModel):
    """Message structure for inter-agent communication."""
    agent_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """Process input and return a message."""
        pass


class RetrievalAgent(BaseAgent):
    """Agent responsible for retrieving relevant documents."""

    def __init__(self, rag_pipeline: RAGPipeline):
        super().__init__("RetrievalAgent")
        self.rag_pipeline = rag_pipeline

    async def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Retrieve relevant documents for the query.
        
        Input: {
            "query": str,
            "top_k": int (optional, default 5),
            "document_filter": List[int] (optional)
        }
        """
        query = input_data.get("query")
        top_k = input_data.get("top_k", 5)
        document_filter = input_data.get("document_filter")

        if not query:
            raise ValueError("Query is required for RetrievalAgent")

        # Retrieve relevant documents
        retrieved_docs = self.rag_pipeline.retrieve_context(
            query=query,
            top_k=top_k,
            document_filter=document_filter
        )

        return AgentMessage(
            agent_name=self.name,
            content=json.dumps([
                {
                    "content": doc["content"],
                    "source": doc["metadata"].get("file_name", "Unknown"),
                    "relevance": doc["relevance_score"]
                }
                for doc in retrieved_docs
            ]),
            metadata={
                "retrieved_count": len(retrieved_docs),
                "query": query
            }
        )


class ContextualizationAgent(BaseAgent):
    """Agent responsible for organizing and structuring retrieved context."""

    async def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Organize and structure the retrieved documents.
        
        Input: {
            "query": str,
            "retrieved_documents": str (JSON string from RetrievalAgent),
            "original_question": str
        }
        """
        query = input_data.get("query", "")
        retrieved_docs_str = input_data.get("retrieved_documents", "[]")
        original_question = input_data.get("original_question", query)

        try:
            retrieved_docs = json.loads(retrieved_docs_str)
        except json.JSONDecodeError:
            retrieved_docs = []

        # Create contextualization prompt
        prompt = ChatPromptTemplate.from_template(
            """You are a document organization specialist. Your task is to organize the retrieved documents 
            into a coherent, structured context that directly answers the student's question.
            
            Student Question: {question}
            
            Retrieved Documents:
            {documents}
            
            Please organize these documents into a clear structure that:
            1. Groups related information together
            2. Removes redundancy
            3. Highlights the most relevant parts
            4. Maintains reference to original sources
            
            Output a well-organized context."""
        )

        # Format documents for LLM
        formatted_docs = "\n\n".join([
            f"Source: {doc.get('source', 'Unknown')}\nContent: {doc.get('content', '')}"
            for doc in retrieved_docs
        ])

        # Call LLM
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "question": original_question,
            "documents": formatted_docs if formatted_docs else "No documents retrieved"
        })

        return AgentMessage(
            agent_name=self.name,
            content=response.content,
            metadata={
                "query": query,
                "documents_processed": len(retrieved_docs)
            }
        )


class AnswerGenerationAgent(BaseAgent):
    """Agent responsible for generating the final answer."""

    async def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Generate a comprehensive answer based on organized context.
        
        Input: {
            "original_question": str,
            "organized_context": str,
            "retrieved_documents": str (JSON)
        }
        """
        original_question = input_data.get("original_question", "")
        organized_context = input_data.get("organized_context", "")
        retrieved_docs_str = input_data.get("retrieved_documents", "[]")

        try:
            retrieved_docs = json.loads(retrieved_docs_str)
        except json.JSONDecodeError:
            retrieved_docs = []

        # Create answer generation prompt
        prompt = ChatPromptTemplate.from_template(
            """You are an expert tutor with deep knowledge. Your task is to provide a comprehensive, 
            clear, and educational answer to the student's question based ONLY on the provided context.
            
            IMPORTANT RULES:
            1. Answer ONLY based on the provided documents
            2. If the answer cannot be found in the documents, explicitly state that
            3. Provide clear, step-by-step explanations
            4. Use examples from the documents
            5. Be encouraging and supportive in your tone
            
            Student Question: {question}
            
            Organized Context:
            {context}
            
            Please provide a comprehensive, well-structured answer."""
        )

        # Call LLM
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "question": original_question,
            "context": organized_context if organized_context else "No context available"
        })

        # Extract sources
        sources = list(set([doc.get("source", "Unknown") for doc in retrieved_docs]))

        return AgentMessage(
            agent_name=self.name,
            content=response.content,
            metadata={
                "sources": sources,
                "documents_used": len(retrieved_docs),
                "question": original_question
            }
        )


class ValidationAgent(BaseAgent):
    """Agent responsible for validating the accuracy and relevance of answers."""

    async def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Validate the accuracy and relevance of the generated answer.
        
        Input: {
            "original_question": str,
            "generated_answer": str,
            "organized_context": str,
            "retrieved_documents": str (JSON)
        }
        """
        original_question = input_data.get("original_question", "")
        generated_answer = input_data.get("generated_answer", "")
        organized_context = input_data.get("organized_context", "")
        retrieved_docs_str = input_data.get("retrieved_documents", "[]")

        # Create validation prompt
        prompt = ChatPromptTemplate.from_template(
            """You are a quality assurance specialist. Evaluate the provided answer against the source documents.
            
            Student Question: {question}
            
            Generated Answer: {answer}
            
            Source Context: {context}
            
            Please evaluate:
            1. Is the answer grounded in the provided documents?
            2. Is the answer complete and comprehensive?
            3. Are there any factual errors or misinterpretations?
            4. Is the answer clear and well-structured?
            5. How confident are you in this answer? (0.0 to 1.0)
            
            Provide your evaluation in the following JSON format:
            {{
                "is_grounded": boolean,
                "is_complete": boolean,
                "has_errors": boolean,
                "clarity_score": number (0-1),
                "confidence_score": number (0-1),
                "comments": string,
                "recommendations": string
            }}"""
        )

        # Call LLM
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "question": original_question,
            "answer": generated_answer,
            "context": organized_context if organized_context else "No context"
        })

        # Parse validation result
        try:
            validation_result = json.loads(response.content)
        except json.JSONDecodeError:
            validation_result = {
                "is_grounded": True,
                "is_complete": True,
                "has_errors": False,
                "clarity_score": 0.8,
                "confidence_score": 0.8,
                "comments": response.content,
                "recommendations": ""
            }

        return AgentMessage(
            agent_name=self.name,
            content=json.dumps(validation_result),
            metadata={
                "question": original_question,
                "validation_passed": validation_result.get("confidence_score", 0) > 0.6
            }
        )


class AgentOrchestrator:
    """Orchestrates the multi-agent system."""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.retrieval_agent = RetrievalAgent(rag_pipeline)
        self.contextualization_agent = ContextualizationAgent()
        self.answer_generation_agent = AnswerGenerationAgent()
        self.validation_agent = ValidationAgent()

    async def process_query(
        self,
        query: str,
        document_filter: Optional[List[int]] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Process a query through the multi-agent pipeline.
        
        Returns: {
            "answer": str,
            "sources": List[str],
            "confidence": float,
            "validation_passed": bool,
            "validation_details": Dict
        }
        """
        # Step 1: Retrieval Agent
        retrieval_result = await self.retrieval_agent.process({
            "query": query,
            "top_k": 5,
            "document_filter": document_filter
        })

        # Step 2: Contextualization Agent
        contextualization_result = await self.contextualization_agent.process({
            "query": query,
            "retrieved_documents": retrieval_result.content,
            "original_question": query
        })

        # Step 3: Answer Generation Agent
        answer_result = await self.answer_generation_agent.process({
            "original_question": query,
            "organized_context": contextualization_result.content,
            "retrieved_documents": retrieval_result.content
        })

        # Step 4: Validation Agent (optional)
        validation_result = None
        validation_passed = True
        confidence_score = 0.8

        if validate:
            validation_result = await self.validation_agent.process({
                "original_question": query,
                "generated_answer": answer_result.content,
                "organized_context": contextualization_result.content,
                "retrieved_documents": retrieval_result.content
            })

            try:
                validation_data = json.loads(validation_result.content)
                validation_passed = validation_data.get("confidence_score", 0.8) > 0.6
                confidence_score = validation_data.get("confidence_score", 0.8)
            except json.JSONDecodeError:
                pass

        return {
            "answer": answer_result.content,
            "sources": answer_result.metadata.get("sources", []),
            "confidence": confidence_score,
            "validation_passed": validation_passed,
            "validation_details": json.loads(validation_result.content) if validation_result else None,
            "metadata": {
                "retrieval_metadata": retrieval_result.metadata,
                "contextualization_metadata": contextualization_result.metadata,
                "answer_metadata": answer_result.metadata
            }
        }
