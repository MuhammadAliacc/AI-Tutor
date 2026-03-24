# API Testing Guide

## Using Swagger UI

The easiest way to test the API is using the interactive Swagger UI:

1. Start the backend: `uvicorn app.main:app --reload`
2. Visit: `http://localhost:8000/docs`
3. Use the interactive interface to test endpoints

## Using cURL

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Use Token in Requests
```bash
TOKEN="your-access-token-here"

# Get documents
curl http://localhost:8000/api/documents \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Upload Document (Admin)
```bash
TOKEN="your-admin-token"

curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/document.pdf" \
  -F "title=My Document" \
  -F "description=Document description"
```

### 5. Ask a Question
```bash
TOKEN="your-token"

curl -X POST http://localhost:8000/api/queries/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "relevant_documents": null
  }'
```

## Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "student@example.com",
        "password": "password123"
    }
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Ask a question
response = requests.post(
    f"{BASE_URL}/queries/ask",
    headers=headers,
    json={"question": "What is quantum mechanics?"}
)
print(response.json())
```

## Using JavaScript/Node.js

```javascript
const API_BASE = "http://localhost:8000/api";

// Login
const loginResponse = await fetch(`${API_BASE}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "student@example.com",
    password: "password123"
  })
});

const { access_token } = await loginResponse.json();

// Ask question
const queryResponse = await fetch(`${API_BASE}/queries/ask`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${access_token}`
  },
  body: JSON.stringify({
    question: "What is machine learning?"
  })
});

const result = await queryResponse.json();
console.log(result);
```

## Common Requests

### Get User's Query History
```bash
curl http://localhost:8000/api/queries/history \
  -H "Authorization: Bearer $TOKEN"
```

### Get Specific Query
```bash
curl http://localhost:8000/api/queries/{query_id} \
  -H "Authorization: Bearer $TOKEN"
```

### Update Document (Admin)
```bash
curl -X PUT http://localhost:8000/api/documents/{doc_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "is_active": true
  }'
```

### Delete Document (Admin)
```bash
curl -X DELETE http://localhost:8000/api/documents/{doc_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Admin Stats
```bash
curl http://localhost:8000/api/admin/dashboard/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Response Examples

### Successful Query Response
```json
{
  "id": 1,
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence...",
  "source_documents": [
    {
      "name": "Chapter_1_ML_Basics.pdf",
      "type": "document"
    }
  ],
  "confidence_score": 0.85,
  "timestamp": "2024-03-24T10:30:00"
}
```

### Error Response
```json
{
  "detail": "Invalid email or password"
}
```

## Testing WebSocket Chat

```javascript
// Connect to WebSocket
const ws = new WebSocket(
  `ws://localhost:8000/api/queries/ws/client1?token=${token}`
);

ws.onopen = () => {
  // Send query
  ws.send(JSON.stringify({
    type: "query",
    question: "What is quantum computing?"
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Response:", message);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};
```

## Performance Testing

### Load Testing with Apache Bench
```bash
# Test single endpoint (requires valid token)
ab -n 100 -c 10 \
   -H "Authorization: Bearer $TOKEN" \
   http://localhost:8000/api/documents
```

### Load Testing with k6
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  const response = http.get('http://localhost:8000/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
}
```

## Debugging

### Enable Debug Logging
```bash
export PYTHONUNBUFFERED=1
export DEBUG=True
uvicorn app.main:app --log-level debug
```

### Check API Health
```bash
curl http://localhost:8000/health
```

### Check Database Connection
```python
from app.core.database import SessionLocal
db = SessionLocal()
db.execute("SELECT 1")
print("Database connected!")
```

## Rate Limiting (Future Feature)

Once rate limiting is implemented:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711270800
```
