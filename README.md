# StudyDuel - 1-zu-1 Lernabfragen MVP

**StudyDuel** ist eine Web-Applikation für 1-zu-1 Lernabfragen mit strikter Sicherheit: Der Learner lädt PDFs hoch, der Examiner sieht alle Fragen und kontrolliert, welche Frage der Learner zu welchem Zeitpunkt sieht.

## Architektur

**Backend:** Python FastAPI + Uvicorn, In-Memory Speicher
**Frontend:** React + Vite + TypeScript  
**Authentifizierung:** Token-basiert (X-Token Header) mit Role-Checks

## User Flow

1. **Session erstellen:** Learner erstellt Session → erhält `session_code` (8 Zeichen)
2. **Session beitreten:** Examiner joined mit Code
3. **PDFs hochladen:** Learner lädt 1..n PDFs hoch
4. **Fragen generieren:** Backend extrahiert Text → generiert 10 Fragen
5. **Prüfung starten:** Examiner sieht alle Fragen, Learner sieht "Warten..."
6. **Frage freigeben:** Examiner klickt "Reveal" → Learner sieht genau diese Frage
7. **Bewertung:** Examiner markiert ok/meh/fail → Nächste Frage
8. **Summary:** Counts der Bewertungen

## Sicherheit

- **Learner-Endpoints:** Dürfen nur aktuelle Frage oder Locked-State sehen
- **Examiner-Endpoints:** Haben Zugriff auf komplette Fragenliste
- **Token-Validierung:** Jeder Request prüft X-Token Header + Role
- **In-Memory:** Keine persistente Speicherung im MVP (einfach austauschbar)

## Installation & Start

### Backend starten

1. Anforderungen installieren:
```bash
cd backend
pip install -r requirements.txt
```

2. Backend starten:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend läuft auf: `http://localhost:8000`  
API-Dokumentation: `http://localhost:8000/docs`

### Frontend starten

1. Abhängigkeiten installieren:
```bash
cd frontend
npm install
```

2. Development-Server starten:
```bash
npm run dev
```

Frontend läuft auf: `http://localhost:5173`

## API-Übersicht

### Session Management

`POST /session` - Neue Session erstellen  
`POST /session/{id}/join` - Session beitreten (body: `{role: "learner"|"examiner"}`)

### Learner-Endpunkte

`POST /session/{id}/upload` - PDFs hochladen (multipart/form-data)  
`POST /session/{id}/generate` - Fragen generieren (body: `{pdf_texts: {...}}`)  
`GET /session/{id}/current` - Aktuelle Frage abrufen (locked oder revealed)

### Examiner-Endpunkte

`GET /session/{id}/questions` - Alle Fragen + Status abrufen  
`POST /session/{id}/reveal` - Aktuelle Frage freigeben  
`POST /session/{id}/next` - Nächste Frage  
`POST /session/{id}/grade` - Frage bewerten (body: `{index, status: "ok"|"meh"|"fail"}`)

**Authentifizierung:** Alle Requests müssen `X-Token` Header enthalten.

## Datenverwaltung

Sessions werden im RAM gespeichert (Klasse `SessionStore` in `app/models.py`). Jede Session enthält:

- Session-ID (8 Zeichen)
- Token → Role Mapping
- PDF-Metadaten
- Fragenliste (generiert)
- Aktuelle Frage (Index)
- Revealed-Flag (Freigegeben ja/nein)
- Grades (Bewertungen pro Frage)

## PDF-Verarbeitung

Das MVP nutzt **pdfplumber** zur Text-Extraktion:

- Upload wird angenommen
- Text wird extrahiert aus PDF-Seiten
- Fragen werden aus Textabsätzen generiert (z.B. "Erkläre X", "Was ist Y")
- Fallback: 10 generische Platzhalter-Fragen, falls PDF leer

**Achtung:** Im MVP werden PDFs nicht persistent gespeichert - nur der extrahierte Text wird verarbeitet.

## CORS-Konfiguration

Backend erlaubt Requests von Frontend automatisch:
- `http://localhost:5173` (Vite dev-server)
- `http://localhost:3000` (Standard React port)
- `http://localhost:5174`

Für Production: In `app/main.py` `allow_origins` anpassen.

## Fehlerbehandlung

- `404 Session not found` - Session existiert nicht
- `401 Missing X-Token header` - Authentifizierung erforderlich
- `403 Invalid token or insufficient permissions` - Falsche Role
- `400 Invalid role` - Role muss "learner" oder "examiner" sein

## Development

### Struktur Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI App + Endpoints
│   ├── models.py       # SessionData & SessionStore
│   ├── services.py     # BusinessLogic (SessionService)
│   └── utils.py        # Helpers (PDF parsing, Token generation)
└── requirements.txt
```

### Struktur Frontend

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Landing.tsx      # Session erstellen / beitreten
│   │   ├── LearnerPage.tsx  # Upload & Polling
│   │   └── ExaminerPage.tsx # Fragenliste & Controls
│   ├── services/
│   │   └── api.ts           # API Client
│   ├── styles/
│   │   └── App.css          # Styling
│   ├── App.tsx              # Main Component
│   └── main.tsx             # Entry Point
└── package.json
```

## Polling-Mechanismus

Frontend-Learner pollst `/session/{id}/current` alle 1 Sekunde:
- Wenn `revealed: false` → zeige "Warten auf Frage"
- Wenn `revealed: true` → zeige aktuelle Frage
- Wenn `status: completed` → alle Fragen beantwortet

Kein WebSocket nötig, simpel und zuverlässig.

## Zukünftige Erweiterungen

- Persistente Datenbank (z.B. PostgreSQL)
- LLM-basierte Frage-Generierung (z.B. OpenAI API)
- WebSocket für Echtzeit-Updates
- Session-Expiration
- Benutzerregistrierung & Authentifizierung
- Export der Ergebnisse (PDF, CSV)
- Fragen-Bearbeitungs-UI im Examiner-Interface

## Lizenz

MIT
