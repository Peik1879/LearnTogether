"""
StudyDuel Configuration & Extension Guide

Dieses Modul zeigt, wie man das MVP erweitert.
"""

# ============================================================================
# 1. DATABASE INTEGRATION (Beispiel mit SQLAlchemy + PostgreSQL)
# ============================================================================

"""
# requirements.txt hinzufügen:
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
alembic==1.12.0

# Beispiel-Model für PostgreSQL:

from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(8), primary_key=True)
    examiner_token = Column(String(32), unique=True)
    learner_token = Column(String(32), unique=True)
    questions = Column(JSON)  # Liste als JSON
    current_index = Column(Integer, default=0)
    revealed = Column(Boolean, default=False)
    grades = Column(JSON)  # dict als JSON
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)  # Auto-expire nach 24h
    
    class Config:
        arbitrary_types_allowed = True
"""

# ============================================================================
# 2. JWT TOKEN EXPIRATION
# ============================================================================

"""
# requirements.txt hinzufügen:
pyjwt==2.8.0

from datetime import datetime, timedelta
import jwt

SECRET_KEY = "your-secret-key-here"

def create_token(role: str, session_id: str, expires_in_hours: int = 24):
    payload = {
        "role": role,
        "session_id": session_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
"""

# ============================================================================
# 3. ECHTE PDF-VERARBEITUNG MIT GROBEM LLM
# ============================================================================

"""
# requirements.txt hinzufügen:
openai==0.27.0

from openai import OpenAI

client = OpenAI(api_key="sk-...")

def generate_questions_with_llm(text: str, num_questions: int = 10) -> List[str]:
    '''Nutze OpenAI GPT um Fragen zu generieren'''
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Du bist ein Lehrer. Generiere genau {num_questions} Lernfragen aus dem folgenden Text."
            },
            {
                "role": "user",
                "content": f"Text:\\n{text}"
            }
        ],
        temperature=0.7
    )
    
    # Parse response und extrahiere Fragen
    content = response.choices[0].message.content
    questions = [q.strip() for q in content.split("\\n") if q.strip()]
    
    return questions[:num_questions]
"""

# ============================================================================
# 4. REDIS CACHING FÜR IN-MEMORY SESSIONS
# ============================================================================

"""
# requirements.txt hinzufügen:
redis==5.0.0

import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Session in Redis speichern
def save_session_to_redis(session_id: str, session_data: dict):
    redis_client.setex(
        f"session:{session_id}",
        86400,  # 24 Stunden Expiration
        json.dumps(session_data)
    )

# Session aus Redis abrufen
def get_session_from_redis(session_id: str):
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None
"""

# ============================================================================
# 5. WEBSOCKET STATT POLLING
# ============================================================================

"""
# requirements.txt hinzufügen:
python-socketio==5.9.0
python-engineio==4.7.0

from fastapi import WebSocket
from typing import Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages
    finally:
        manager.disconnect(websocket)
"""

# ============================================================================
# 6. LOGGING & AUDIT TRAIL
# ============================================================================

"""
# requirements.txt hinzufügen:
python-json-logger==2.0.7

import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Usage:
logger.info("Session created", extra={
    "session_id": "ABC12345",
    "examiner_token": "xyz...",
    "timestamp": datetime.now().isoformat()
})
"""

# ============================================================================
# 7. RATE LIMITING
# ============================================================================

"""
# requirements.txt hinzufügen:
slowapi==0.1.9

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/session")
@limiter.limit("10/minute")  # Max 10 Sessions pro Minute
def create_session(request: Request):
    ...
"""

# ============================================================================
# 8. DOCKER DEPLOYMENT
# ============================================================================

"""
# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile

FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# docker-compose.yml

version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/studyduel
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=studyduel
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""

# ============================================================================
# 9. TESTING MIT PYTEST
# ============================================================================

"""
# requirements.txt (dev) hinzufügen:
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.24.0

# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import store

client = TestClient(app)

def test_create_session():
    response = client.post("/session")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "examiner_token" in data

def test_join_session():
    # Create session first
    create_response = client.post("/session")
    session_id = create_response.json()["session_id"]
    
    # Join as learner
    response = client.post(
        f"/session/{session_id}/join",
        json={"role": "learner"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "learner"

def test_role_permission_denied():
    create_response = client.post("/session")
    session_id = create_response.json()["session_id"]
    learner_token = client.post(
        f"/session/{session_id}/join",
        json={"role": "learner"}
    ).json()["token"]
    
    # Learner versucht, Fragen abzurufen (sollte fehlschlagen)
    response = client.get(
        f"/session/{session_id}/questions",
        headers={"X-Token": learner_token}
    )
    assert response.status_code == 403

# pytest running:
# pytest backend/tests/ -v
"""

# ============================================================================
# 10. MONITORING & OBSERVABILITY
# ============================================================================

"""
# requirements.txt hinzufügen:
prometheus-client==0.17.0

from prometheus_client import Counter, Histogram, generate_latest

# Metrics
session_created = Counter('sessions_created_total', 'Total sessions created')
pdf_uploaded = Counter('pdfs_uploaded_total', 'Total PDFs uploaded')
question_revealed = Counter('questions_revealed_total', 'Total questions revealed')
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration')

# In endpoints:
@app.post("/session")
async def create_session():
    session_created.inc()
    ...

@app.get("/metrics")
def metrics():
    return generate_latest()
"""

print("✓ Configuration & Extension Guide geladen")
print("✓ Alle 10 Erweiterungsmodule verfügbar")
