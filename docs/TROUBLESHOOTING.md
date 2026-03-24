# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. "ModuleNotFoundError: No module named 'app'"
**Cause**: Virtual environment not activated or wrong directory

**Solution**:
```bash
# Ensure you're in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Verify installation
pip list | grep fastapi
```

#### 2. "OPENAI_API_KEY not set"
**Cause**: Environment variable not configured

**Solution**:
```bash
# Edit .env file
nano .env

# Add your API key
OPENAI_API_KEY=sk-your-key-here

# Verify
echo $OPENAI_API_KEY
```

#### 3. "Could not connect to database"
**Cause**: PostgreSQL not running or wrong connection string

**Solution**:
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT 1"

# If not running:
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Windows: Start PostgreSQL service

# Check DATABASE_URL in .env
# Format: postgresql://user:password@localhost:5432/ai_tutor
```

#### 4. "Port 8000 already in use"
**Cause**: Another process using the port

**Solution**:
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### 5. "Chromadb collection not found"
**Cause**: Vector database not initialized

**Solution**:
```bash
# Remove old chroma database
rm -rf data/chroma_db/

# Restart server - it will recreate
uvicorn app.main:app --reload
```

#### 6. "No documents returned from search"
**Cause**: Documents not properly ingested or embeddings failed

**Solution**:
```python
# Check in Python shell
from app.rag.pipeline import RAGPipeline
rag = RAGPipeline()

# Try searching
results = rag.retrieve_context("test query")
print(len(results))  # Should be > 0

# If 0, need to upload documents first
```

#### 7. "CORS error when calling API from frontend"
**Cause**: CORS headers not configured correctly

**Solution**:
```bash
# In .env, ensure ALLOWED_ORIGINS includes frontend URL
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Restart backend
```

#### 8. "JWT token expired/invalid"
**Cause**: Token creation or validation issue

**Solution**:
```python
# Generate new token
from app.services.user_service import UserService
from app.core.database import SessionLocal

db = SessionLocal()
user_service = UserService(db)
user = user_service.get_user_by_email("student@example.com")
token = user_service.create_access_token(user)
print(token)
```

---

### Frontend Issues

#### 1. "Cannot find module 'react'"
**Cause**: Dependencies not installed

**Solution**:
```bash
cd frontend
npm install

# or if that doesn't work:
rm -rf node_modules package-lock.json
npm install
```

#### 2. "Port 3000 already in use"
**Cause**: Another process using the port

**Solution**:
```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
npm run dev -- --port 3001
```

#### 3. "API requests timeout or 404"
**Cause**: Backend not running or wrong URL

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# If not running, start it:
cd backend
uvicorn app.main:app --reload

# Check VITE_API_BASE_URL in .env.local
cat .env.local

# Should be: VITE_API_BASE_URL=http://localhost:8000/api
```

#### 4. "Message component not rendering"
**Cause**: Markdown dependency missing

**Solution**:
```bash
npm install react-markdown remark-gfm
npm run dev
```

#### 5. "Authentication not working"
**Cause**: Token not being stored or sent correctly

**Solution**:
```javascript
// Check localStorage
console.log(localStorage.getItem('token'));
console.log(localStorage.getItem('user'));

// Check API call in Network tab of DevTools
// Authorization header should be: "Bearer <token>"
```

#### 6. "Tailwind styles not applied"
**Cause**: CSS not compiled or purge issue

**Solution**:
```bash
# Rebuild CSS
npm run build

# or restart dev server
npm run dev
```

---

### Database Issues

#### 1. "Connection pool exhausted"
**Cause**: Too many open connections

**Solution**:
```python
# In app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### 2. "Relation does not exist"
**Cause**: Database tables not created

**Solution**:
```bash
# Create tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# or with migrations (if using Alembic)
alembic upgrade head
```

#### 3. "Deadlock detected"
**Cause**: Transaction conflicts

**Solution**:
```python
# Add retry logic
from sqlalchemy.exc import IntegrityError
import time

for attempt in range(3):
    try:
        # your code
        break
    except IntegrityError:
        time.sleep(0.1 * (2 ** attempt))
        if attempt == 2:
            raise
```

---

### Docker Issues

#### 1. "Container exits immediately"
**Cause**: Application error on startup

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Run container interactively
docker-compose run backend bash

# Check migrations
docker-compose exec backend python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

#### 2. "Cannot connect between containers"
**Cause**: Network or service naming issue

**Solution**:
```yaml
# In docker-compose.yml, ensure service name is correct
services:
  postgres:
    container_name: ai-tutor-db
    
  backend:
    # Connection string should be:
    # postgresql://user:pass@postgres:5432/ai_tutor
    # (not localhost, use service name)
```

#### 3. "Permission denied errors"
**Cause**: File permissions in volume mounts

**Solution**:
```bash
# Fix directory permissions
chmod -R 755 ./uploads
chmod -R 755 ./data

# Or run with different user in docker-compose.yml
services:
  backend:
    user: "1000:1000"
```

---

### Performance Issues

#### 1. "Slow API responses"
**Cause**: Vector search is slow

**Solution**:
```python
# Adjust chunk size for faster retrieval
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Smaller chunks
    chunk_overlap=100
)

# Use top_k to limit results
results = rag.retrieve_context(query, top_k=3)
```

#### 2. "High memory usage"
**Cause**: Large embeddings or documents

**Solution**:
```python
# Use streaming instead of loading all
# Adjust vector store batch size
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=chunks,
    metadatas=metadatas,
    batch_size=100  # Process in batches
)
```

#### 3. "OpenAI API rate limits"
**Cause**: Too many requests

**Solution**:
```python
import time
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
async def call_openai_api():
    # Your API call
    pass
```

---

### Integration Issues

#### 1. "Agent orchestrator timeout"
**Cause**: LLM taking too long

**Solution**:
```python
# Set timeout
from langchain.callbacks.base import BaseCallbackHandler

llm = ChatOpenAI(
    timeout=30,  # seconds
    request_timeout=30
)
```

#### 2. "Document not indexed properly"
**Cause**: File format not supported

**Solution**:
```bash
# Check supported formats in .env
ALLOWED_FILE_TYPES=pdf,docx,txt,md

# Verify file can be parsed
python -c "
from app.rag.pipeline import DocumentLoader
loader = DocumentLoader()
chunks = loader.load_document('file.pdf', 'pdf')
print(f'Loaded {len(chunks)} chunks')
"
```

---

## Debugging Techniques

### Enable Verbose Logging
```bash
# Backend
export PYTHONUNBUFFERED=1
export LOGLEVEL=DEBUG
uvicorn app.main:app --log-level debug

# Frontend
export DEBUG=true
npm run dev
```

### Use Python Debugger
```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json:
{
    "name": "Python: FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": ["app.main:app", "--reload"],
    "jinja": true,
    "justMyCode": true
}
```

### Check System Resources
```bash
# Memory
free -h
df -h

# Running processes
ps aux | grep python

# Network connections
netstat -tlnp | grep :8000
```

### Database Inspection
```bash
# Connect to database
psql -U aiuser -d ai_tutor

# Check tables
\dt

# Check data
SELECT * FROM users;
SELECT COUNT(*) FROM documents;
```

---

## Prevention

### Regular Monitoring
- Set up log aggregation (ELK, Datadog)
- Monitor resource usage
- Track error rates
- Monitor API latency

### Testing
- Write unit tests
- Integration tests
- Load tests
- Smoke tests before deployment

### Backups
- Daily automated database backups
- Document storage backups
- Configuration versioning

### Documentation
- Document any custom fixes
- Keep runbooks updated
- Document deployment process
- Create incident reports

---

## Getting Help

1. **Check logs**: Application logs often have the answer
2. **Search issues**: GitHub issues or Stack Overflow
3. **Check documentation**: API docs and guides
4. **Ask community**: Forums or discussion boards
5. **Contact support**: For commercial support options
