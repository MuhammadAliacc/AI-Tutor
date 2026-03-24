FROM python:3.11-slim

WORKDIR /app

# Install system deps (IMPORTANT for hnswlib)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads data logs

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]