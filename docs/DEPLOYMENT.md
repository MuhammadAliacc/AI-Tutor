# Deployment Guide

## Pre-Deployment Checklist

- [ ] Update `.env` with production values
- [ ] Set `DEBUG=False` in backend
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper database credentials
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS origins
- [ ] Set up logging and monitoring
- [ ] Configure database backups
- [ ] Test all features in staging
- [ ] Plan rollback strategy

## Environment Variables

### Backend Production `.env`
```
# Database
DATABASE_URL=postgresql://user:secure_password@db-host:5432/ai_tutor

# Security
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL=gpt-4

# Server
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload
UPLOAD_DIRECTORY=/var/ai_tutor_uploads
MAX_FILE_SIZE=52428800

# Vector Store
VECTOR_STORE_TYPE=chroma
CHROMA_PATH=/var/ai_tutor_data/chroma_db
```

## Docker Deployment

### Build Images
```bash
# Build backend image
docker build -t ai-tutor-backend:latest ./backend

# Build frontend image
docker build -t ai-tutor-frontend:latest ./frontend
```

### Push to Registry
```bash
# Docker Hub
docker tag ai-tutor-backend:latest your-username/ai-tutor-backend:latest
docker push your-username/ai-tutor-backend:latest

docker tag ai-tutor-frontend:latest your-username/ai-tutor-frontend:latest
docker push your-username/ai-tutor-frontend:latest
```

### Docker Compose for Production
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ai_tutor
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ai-tutor-backend:latest
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/ai_tutor
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "False"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ai_tutor_uploads:/app/uploads
      - ai_tutor_data:/app/data

  frontend:
    image: ai-tutor-frontend:latest
    restart: always
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: https://api.yourdomain.com

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  ai_tutor_uploads:
  ai_tutor_data:
```

## Nginx Configuration

### Basic Nginx Setup
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/queries/ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## AWS Deployment

### Using ECS
1. Create ECR repositories
2. Push images to ECR
3. Create ECS task definitions
4. Launch ECS services
5. Configure RDS for database
6. Set up S3 for file uploads
7. Configure ALB for load balancing

### Using Elastic Beanstalk
1. Prepare deployment package
2. Configure environment
3. Deploy with `eb deploy`
4. Monitor with CloudWatch

## Google Cloud Deployment

### Using Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-tutor

# Deploy
gcloud run deploy ai-tutor \
  --image gcr.io/PROJECT_ID/ai-tutor \
  --platform managed \
  --region us-central1
```

### Using Kubernetes
```bash
# Create deployment
kubectl apply -f deployment.yaml

# Create service
kubectl apply -f service.yaml

# Configure ingress
kubectl apply -f ingress.yaml
```

## Azure Deployment

### Using App Service
```bash
# Login
az login

# Create resource group
az group create --name ai-tutor-rg --location eastus

# Create App Service plan
az appservice plan create --name ai-tutor-plan \
  --resource-group ai-tutor-rg

# Deploy
az webapp deployment source config-zip \
  --resource-group ai-tutor-rg \
  --name ai-tutor \
  --src deployment.zip
```

## Database Backups

### PostgreSQL Backup
```bash
# Backup
pg_dump -U aiuser ai_tutor > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore
psql -U aiuser ai_tutor < backup.sql
```

### Automated Backups (cron)
```bash
# Add to crontab
0 2 * * * pg_dump -U aiuser ai_tutor | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz
```

## Monitoring & Logging

### Application Logging
```python
# In app/core/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="/var/log/ai_tutor/app.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Metrics to Monitor
- API response times
- Database query times
- Error rates
- Vector search latency
- Token usage (OpenAI)
- Database connections

### Tools
- **Datadog**: Full monitoring stack
- **New Relic**: APM monitoring
- **ELK Stack**: Logging
- **Prometheus + Grafana**: Metrics

## Security Hardening

### SSL/TLS
- Use Let's Encrypt for free certificates
- Force HTTPS only
- Set HSTS headers

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/queries/ask")
@limiter.limit("10/minute")
async def ask_query(...):
    pass
```

### CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Zero-Downtime Deployment

### Blue-Green Deployment
1. Deploy new version to green environment
2. Run smoke tests
3. Switch traffic to green
4. Keep blue as rollback

### Canary Deployment
1. Deploy to small % of servers
2. Monitor metrics
3. Gradually increase traffic
4. Full rollout on success

## Rollback Procedure

1. Store previous version tag
2. Update deployment to previous tag
3. Scale down new version
4. Verify application works
5. Investigate issue

## Scaling

### Horizontal Scaling
- Load balance requests across multiple servers
- Use database connection pooling
- Cache frequently accessed data

### Vertical Scaling
- Increase server resources
- Optimize queries
- Use faster hardware

## Cost Optimization

- Use reserved instances
- Auto-scale based on demand
- Optimize database queries
- Cache API responses
- Use CDN for static assets
