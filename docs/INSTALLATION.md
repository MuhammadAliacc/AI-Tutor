# Installation and Setup Guide

## Prerequisites

### Required Software
- Python 3.10 or higher
- Node.js 18+ and npm
- PostgreSQL 13+
- Git

### Required Accounts
- OpenAI API key (for GPT models and embeddings)

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Important Environment Variables**:
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_tutor

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Server
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Step 5: Initialize Database
```bash
# Create tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Step 6: Create Admin User (Optional)
```bash
python scripts/create_admin.py
```

### Step 7: Run Backend Server
```bash
# With hot reload (development)
uvicorn app.main:app --reload

# Without hot reload (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment (Optional)
```bash
# Create .env.local if you need custom API base URL
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.local
```

### Step 4: Run Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Step 5: Build for Production
```bash
npm run build
npm run preview
```

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Step 1: Update Environment
```bash
cp .env.example .env
# Edit .env with your settings (especially OPENAI_API_KEY)
```

### Step 2: Build and Run
```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 3: Initialize Database
```bash
# Run migrations
docker-compose exec backend python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Accessing Services
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Database: `localhost:5432`

### Stopping Services
```bash
docker-compose down

# Remove data volumes
docker-compose down -v
```

## PostgreSQL Setup (Local)

### macOS (Using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL service
brew services start postgresql

# Create database
createdb ai_tutor

# Create user
psql -c "CREATE USER aiuser WITH PASSWORD 'aipass123';"
psql -c "ALTER USER aiuser CREATEDB;"
```

### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres createdb ai_tutor
sudo -u postgres createuser -P aiuser
```

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run installer
3. Remember the password for superuser
4. Use pgAdmin to create database and user

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### Import Errors
```bash
# Ensure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U aiuser -d ai_tutor -c "SELECT 1"

# Check DATABASE_URL in .env
# Format: postgresql://user:password@host:port/database
```

#### OpenAI API Error
```
Error: Invalid API key
→ Check OPENAI_API_KEY in .env
→ Get key from https://platform.openai.com/api-keys
→ Check account has sufficient credits
```

### Frontend Issues

#### Port Already in Use
```bash
# Kill process on port 3000
lsof -i :3000
kill -9 <PID>
```

#### API Connection Error
```
Error: Cannot reach API
→ Ensure backend is running (http://localhost:8000)
→ Check VITE_API_BASE_URL in .env.local
→ Check CORS settings in backend/.env
```

#### Module Not Found
```bash
# Clear node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Docker Issues

#### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up
```

#### Database Migration Failed
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Verification

### Backend Verification
```bash
# Check health endpoint
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

### Frontend Verification
- Navigate to `http://localhost:3000`
- Should see login page
- Try logging in with:
  - Email: `student@example.com`
  - Password: `password123`

### API Verification
```bash
# Get API docs
curl http://localhost:8000/docs

# Should open interactive API documentation
```

## Next Steps

1. **Upload Documents**: Log in as admin and upload PDFs/DOCX
2. **Ask Questions**: Log in as student and chat with AI tutor
3. **Monitor Analytics**: View stats in admin dashboard
4. **Customize Settings**: Update config in `.env`

## Getting Help

- **API Issues**: Check `/docs` endpoint
- **Database Issues**: Check PostgreSQL logs
- **LLM Issues**: Check OpenAI dashboard for quota/errors
- **General Issues**: Check application logs in console

## Security Reminders

⚠️ **Before Production**:
1. Change `SECRET_KEY` in `.env`
2. Use strong database password
3. Enable HTTPS/SSL
4. Set `DEBUG=False`
5. Configure proper CORS origins
6. Use environment-specific configs
7. Set up proper logging
8. Enable database backups
