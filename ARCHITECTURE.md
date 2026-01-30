# StudyDuel - Projektstruktur

```
LearnTogether/
│
├── README.md                    # Hauptdokumentation
├── TESTING.md                   # Testing & Debug-Guide
│
├── backend/                     # FastAPI Backend
│   ├── requirements.txt         # Python Dependencies
│   ├── .gitignore
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI App + API Endpoints
│       ├── models.py            # SessionData + SessionStore (In-Memory)
│       ├── services.py          # SessionService (Business Logic)
│       └── utils.py             # Utility Functions (PDF, Tokens, Questions)
│
└── frontend/                    # React + Vite + TypeScript
    ├── package.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── index.html
    ├── .gitignore
    └── src/
        ├── main.tsx             # Entry Point
        ├── App.tsx              # Main Component
        ├── pages/
        │   ├── Landing.tsx      # Session erstellen / beitreten
        │   ├── LearnerPage.tsx  # PDF Upload + Polling
        │   └── ExaminerPage.tsx # Fragenliste + Controls
        ├── services/
        │   └── api.ts           # API Client (axios)
        └── styles/
            └── App.css          # Styling (responsive)
```

## Schnellstart

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Browser: http://localhost:5173
```

## Key Features

✓ Session-basiert mit 8-Zeichen-Codes  
✓ Token-authentifizierung (X-Token Header)  
✓ Learner-Sicherheit: Fragenliste nicht einsehbar  
✓ PDF-Upload mit Text-Extraktion (pdfplumber)  
✓ Auto-Fragengenerierung (10 Fragen)  
✓ Polling-basierte Echtzeit (1s Intervall)  
✓ In-Memory Storage (MVP, leicht erweiterbar)  
✓ Modern React UI mit Responsive Design  
✓ CORS konfiguriert  
✓ Error Handling + Role-based Access Control  

## Architektur-Highlights

### Backend

- **SessionStore:** Global in-memory dict mit SessionData objekten
- **SessionService:** Zentrale Business-Logic
- **Endpoints:** Strict role-checking via Token-Validierung
- **Security:** Learner-GET /current verrät nie komplette Fragenliste

### Frontend

- **Landing:** Session-UI (create/join)
- **LearnerPage:** Upload + Polling Loop
- **ExaminerPage:** Fragenliste + Bewertungs-Controls
- **API Service:** Wrapper um axios mit Token-Handling

## Nächste Schritte (Production)

1. Replace In-Memory → PostgreSQL + SQLAlchemy
2. Add JWT Token Expiration
3. Implementiere echte User-Authentifizierung
4. Add LLM-basierte Fragengenerierung (OpenAI)
5. WebSocket statt Polling
6. Session-Persistence (Redis)
7. Audit Logging
8. Rate Limiting

Viel Erfolg! 🚀
