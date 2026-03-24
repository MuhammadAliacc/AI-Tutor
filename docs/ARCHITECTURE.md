# API Architecture & Design

## Overview
The AI Tutor backend uses a sophisticated multi-layered architecture with clear separation of concerns.

## Architecture Layers

### 1. API Layer (`app/api/`)
FastAPI endpoints organized by feature:
- **auth.py**: Authentication (login, registration)
- **documents.py**: Document CRUD operations
- **queries.py**: Query processing and chat
- **admin.py**: Admin dashboard and management

**Key Features**:
- JWT token-based auth
- Role-based access control
- Request/Response validation with Pydantic
- WebSocket support for real-time chat

### 2. Service Layer (`app/services/`)
Business logic and orchestration:
- **user_service.py**: User management and authentication
- **document_service.py**: Document lifecycle management
- **query_service.py**: Query processing and history

**Responsibilities**:
- Coordinate between API and models
- Implement business rules
- Handle transactions
- Manage RAG pipeline integration

### 3. Agent Layer (`app/agents/`)
Multi-agent AI orchestration:
- **orchestrator.py**: Main agent coordinator
  - RetrievalAgent: Vector search and document retrieval
  - ContextualizationAgent: Info structuring and organization
  - AnswerGenerationAgent: Final answer generation
  - ValidationAgent: Quality assurance

**Agent Communication**:
- Agents pass structured `AgentMessage` objects
- Sequential pipeline: Retrieval → Contextualization → Generation → Validation
- Each agent can access previous results

### 4. RAG Layer (`app/rag/`)
Retrieval-Augmented Generation pipeline:
- **pipeline.py**:
  - DocumentLoader: Handle PDF/DOCX/TXT parsing
  - VectorStore: Chromadb embeddings management
  - RAGPipeline: Main RAG orchestrator

**Features**:
- Recursive text chunking (1000 chars, 200 overlap)
- OpenAI embeddings integration
- Similarity-based retrieval (top-k)
- Document metadata tracking

### 5. Data Layer
Database and persistence:
- **Models** (`app/models/database.py`):
  - User: Authentication and roles
  - Document: Uploaded materials
  - DocumentChunk: Vector chunks
  - Query: Audit trail
- **Database** (`app/core/database.py`):
  - SQLAlchemy ORM
  - PostgreSQL

### 6. Core Layer (`app/core/`)
Cross-cutting concerns:
- **config.py**: Environment configuration
- **database.py**: Database setup
- **security.py**: JWT and password hashing

## Data Flow

### Query Processing Flow
```
User Question
    ↓
API Endpoint (/api/queries/ask)
    ↓
QueryService
    ↓
AgentOrchestrator
    ├→ RetrievalAgent (Search documents)
    ├→ ContextualizationAgent (Organize context)
    ├→ AnswerGenerationAgent (Generate answer)
    ├→ ValidationAgent (Validate quality)
    ↓
Response with sources & confidence
    ↓
Stored in Query model (audit trail)
```

### Document Upload Flow
```
File Upload
    ↓
DocumentService
    ├→ Save file to disk
    ├→ Create Document model
    ├→ DocumentLoader (parse & chunk)
    ├→ VectorStore (embed & index)
    ↓
Document ready for retrieval
```

## Key Design Patterns

### 1. Dependency Injection
- Services receive dependencies via constructor
- RAGPipeline injected into services/agents
- Database session from FastAPI dependencies

### 2. Service Pattern
- Each service handles specific domain
- Clear boundaries and responsibilities
- Reusable business logic

### 3. Repository Pattern
- Database operations encapsulated
- Services work with models, not raw queries

### 4. Agent Pattern
- Multi-agent orchestration
- Each agent has defined role
- Agents communicate via messages

## API Security

### Authentication
1. User registers with email/password
2. Password hashed with bcrypt
3. Login returns JWT token
4. Token required for protected endpoints
5. Token decoded to extract user info

### Authorization
1. **Roles**: ADMIN, STUDENT
2. **Admin-only endpoints**:
   - POST /api/documents/upload
   - PUT /api/documents/{id}
   - DELETE /api/documents/{id}
   - GET /api/admin/*
3. **Student access**:
   - GET documents (read-only)
   - POST /api/queries/ask
   - GET /api/queries/history

## Performance Considerations

### Caching
- Embeddings computed once, stored in Chromadb
- Document chunks indexed for O(log n) retrieval

### Async Operations
- FastAPI async endpoints
- WebSocket support for real-time updates
- Background processing capability

### Database
- Indexes on frequently queried fields
- Connection pooling
- Query optimization

## Error Handling

### Validation
- Pydantic schemas validate all inputs
- File type and size validation
- Token validation

### Error Responses
- Standardized HTTP status codes
- Meaningful error messages
- Request ID for debugging

## Extension Points

### Adding New Agents
1. Create class inheriting from BaseAgent
2. Implement `async process(input_data)` method
3. Add to AgentOrchestrator
4. Update orchestration pipeline

### Adding New File Types
1. Extend DocumentLoader.load_document()
2. Add parsing logic for new format
3. Update ALLOWED_FILE_TYPES

### Custom LLM Models
1. Change OPENAI_MODEL in config
2. Update ChatOpenAI initialization
3. Adjust temperature/parameters as needed
