# Getting Started with AI Tutor

## Quick Start (5 minutes)

### 1. Install Prerequisites
```bash
# Check you have:
python3 --version  # 3.10+
npm --version      # 18+
psql --version     # 13+
```

### 2. Backend Setup
```bash
cd backend

# Create environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database
python init_db.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Start Backend (in another terminal)
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 5. Access Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Demo Login Credentials

```
Admin User:
  Email: admin@example.com
  Password: adminpass123

Student User:
  Email: student@example.com
  Password: password123
```

## First Steps

### As an Admin:

1. **Login** with admin credentials
2. **Go to Dashboard** - See system statistics
3. **Go to Documents** - Upload a PDF or document
   - Click "Upload Document"
   - Select a file
   - Add title and description
   - Click "Upload Document"
4. **Verify Upload** - Document appears in the list

### As a Student:

1. **Login** with student credentials
2. **Go to Chat** - Main interface
3. **Ask a Question**
   - Type a question about the uploaded materials
   - Click "Send" or press Ctrl+Enter
   - Wait for the AI response
4. **View Sources** - See which documents were used
5. **Check History** - View past questions

## Key Features Explained

### 🎓 Chat Interface
- Ask questions about uploaded learning materials
- Get answers grounded in real documents
- See source materials for each answer
- View conversation history

### 📄 Document Management (Admin)
- Upload PDFs, DOCX, TXT files
- Add titles and descriptions
- Delete documents
- Manage student access (students can't download)

### 🤖 AI Features
- Four-agent system working together:
  1. **Retrieval Agent**: Finds relevant documents
  2. **Contextualization Agent**: Organizes information
  3. **Answer Generation Agent**: Creates answers
  4. **Validation Agent**: Ensures quality

### 📊 Admin Dashboard
- View system statistics
- Monitor document storage
- Track query usage
- See system health

## Configuration Guide

### Database Setup
```bash
# PostgreSQL connection
# Edit .env:
DATABASE_URL=postgresql://user:password@localhost:5432/ai_tutor

# Or use SQLite for testing:
DATABASE_URL=sqlite:///./test.db
```

### OpenAI API Key
```bash
# Get key from https://platform.openai.com/api-keys
# Add to .env:
OPENAI_API_KEY=sk-your-key-here

# Choose model:
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

### Allowed Origins (CORS)
```bash
# For local development:
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# For production:
ALLOWED_ORIGINS=https://yourdomain.com
```

## Project Structure at a Glance

```
AI-Tutor/
├── backend/           # Python FastAPI server
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── agents/    # AI agents
│   │   ├── rag/       # Document retrieval
│   │   ├── services/  # Business logic
│   │   └── models/    # Database
│   └── requirements.txt
│
├── frontend/          # React application
│   ├── src/
│   │   ├── pages/     # Pages (Chat, Auth, Admin)
│   │   ├── components/# Reusable components
│   │   ├── services/  # API calls
│   │   └── store/     # State management
│   └── package.json
│
└── docs/              # Documentation
    ├── INSTALLATION.md
    ├── ARCHITECTURE.md
    ├── API_TESTING.md
    └── DEPLOYMENT.md
```

## Common Tasks

### Upload a Document
1. Login as admin
2. Click "Documents" in navbar
3. Fill in title and description
4. Select file
5. Click "Upload Document"
6. Wait for success message

### Ask a Question
1. Login as student
2. Click "Chat" in navbar
3. Type question in input box
4. Press Ctrl+Enter or click Send
5. Wait for response
6. Source documents shown in answer

### View Statistics
1. Login as admin
2. Click "Dashboard"
3. View cards with stats
4. See recent queries

### Delete a Document
1. Login as admin
2. Go to "Documents"
3. Find document in table
4. Click Trash icon
5. Confirm deletion

## Useful Commands

### Backend
```bash
# Install new package
pip install package-name
pip freeze > requirements.txt

# Run specific test
pytest app/tests/test_auth.py

# Database shell
python -c "from app.core.database import SessionLocal; db = SessionLocal(); print('Connected!')"
```

### Frontend
```bash
# Install new package
npm install package-name

# Build for production
npm run build

# Run production build locally
npm run preview

# Lint code
npm run lint
```

### Docker
```bash
# Start all services
docker-compose up

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build --no-cache
```

## Troubleshooting

### API not responding
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend
cd backend && uvicorn app.main:app --reload
```

### Database error
```bash
# Initialize database
python init_db.py

# Check PostgreSQL
psql -U aiuser -d ai_tutor -c "SELECT 1"
```

### Document upload fails
- Check file size (max 50MB)
- Ensure file format is PDF, DOCX, or TXT
- Check disk space
- Look at backend logs

### AI doesn't respond
- Verify OPENAI_API_KEY is set
- Check OpenAI account has credits
- Look at API errors in logs

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Read Architecture**: See `docs/ARCHITECTURE.md`
3. **Setup Production**: See `docs/DEPLOYMENT.md`
4. **Review Code**: Start with `backend/app/main.py`
5. **Customize**: Modify colors, messages, models

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **LangChain Docs**: https://python.langchain.com
- **OpenAI Docs**: https://platform.openai.com/docs

## Need Help?

1. Check the docs in `/docs` folder
2. Review error messages in logs
3. Search similar issues online
4. Check API documentation at /docs endpoint
5. Reference the TROUBLESHOOTING guide

## Security Notes

⚠️ **Before deploying to production**:
- Change SECRET_KEY in .env
- Use strong database password
- Enable HTTPS/SSL
- Configure proper CORS
- Set DEBUG=False
- Backup database regularly
- Monitor logs and errors

## Performance Tips

- Keep documents focused and relevant
- Upload documents of reasonable size
- Use PostgreSQL (not SQLite) for production
- Enable caching in frontend
- Monitor OpenAI API usage
- Optimize database queries

## Contributing

Want to improve AI Tutor?
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit a pull request

Enjoy using AI Tutor! 🚀
