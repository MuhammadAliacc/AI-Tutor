"""Main FastAPI application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import settings
from app.core.database import Base, engine
from app.api import auth, documents, queries, admin
from app.schemas.schemas import HealthCheck


# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    print("Starting AI Tutor application...")
    yield
    # Shutdown
    print("Shutting down AI Tutor application...")


app = FastAPI(
    title="AI Tutor API",
    description="Full-stack AI Tutor with RAG and multi-agent architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(queries.router)
app.include_router(admin.router)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Tutor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
