# StudyDuel API Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Alle Requests (außer `/session` und `/session/{id}/join`) benötigen:
```
Header: X-Token: <token>
```

---

## Session Management

### POST /session
Neue Session erstellen

**Request:**
```bash
curl -X POST http://localhost:8000/session
```

**Response (200 OK):**
```json
{
  "session_id": "ABC12345",
  "examiner_token": "examiner_token_xyz..."
}
```

---

### POST /session/{session_id}/join
Session beitreten (Learner oder Examiner)

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/join \
  -H "Content-Type: application/json" \
  -d '{"role": "learner"}'
```

**Roles:**
- `"learner"` - Learner (eingeschränkter Zugriff)
- `"examiner"` - Examiner (voller Zugriff)

**Response (200 OK):**
```json
{
  "token": "learner_token_xyz...",
  "role": "learner"
}
```

---

## Learner Endpoints

### POST /session/{session_id}/upload
PDFs hochladen

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/upload \
  -H "X-Token: <learner_token>" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "uploaded": 2,
  "files": ["document1.pdf", "document2.pdf"]
}
```

**Errors:**
- `400` - Keine Dateien oder nicht PDF-Format
- `403` - Insufficient permissions (nur Learner)

---

### POST /session/{session_id}/generate
Fragen aus PDFs generieren

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/generate \
  -H "X-Token: <learner_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_texts": {
      "document.pdf": "Extrahierter Text aus PDF..."
    }
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "question_count": 10
}
```

---

### GET /session/{session_id}/current
Aktuelle Frage abrufen (Locked oder Revealed)

**Request:**
```bash
curl -X GET http://localhost:8000/session/ABC12345/current \
  -H "X-Token: <learner_token>"
```

**Response wenn locked (200 OK):**
```json
{
  "status": "locked",
  "index": 0,
  "total": 10
}
```

**Response wenn revealed (200 OK):**
```json
{
  "status": "revealed",
  "index": 0,
  "question": "Erkläre: Der Fotosynthese-Prozess",
  "total": 10
}
```

**Response wenn completed (200 OK):**
```json
{
  "status": "completed",
  "index": 10,
  "total": 10
}
```

---

## Examiner Endpoints

### GET /session/{session_id}/questions
Alle Fragen + Status abrufen

**Request:**
```bash
curl -X GET http://localhost:8000/session/ABC12345/questions \
  -H "X-Token: <examiner_token>"
```

**Response (200 OK):**
```json
{
  "session_id": "ABC12345",
  "questions": [
    "Erkläre: Die Photosynthese",
    "Was bedeutet: Chlorophyll?",
    "Erkläre: Der Kohlenstoffkreislauf"
  ],
  "current_index": 0,
  "revealed": false,
  "grades": {},
  "pdfs": [
    {"filename": "biology.pdf", "size": 2048576}
  ]
}
```

**Errors:**
- `403` - Insufficient permissions (nur Examiner)
- `404` - Session not found

---

### POST /session/{session_id}/reveal
Aktuelle Frage freigeben (Learner kann sie nun sehen)

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/reveal \
  -H "X-Token: <examiner_token>"
```

**Response (200 OK):**
```json
{
  "status": "revealed"
}
```

---

### POST /session/{session_id}/next
Nächste Frage anzeigen

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/next \
  -H "X-Token: <examiner_token>"
```

**Response (200 OK):**
```json
{
  "status": "success"
}
```

**Errors:**
- `400` - Keine weiteren Fragen oder Session not found

---

### POST /session/{session_id}/grade
Frage bewerten

**Request:**
```bash
curl -X POST http://localhost:8000/session/ABC12345/grade \
  -H "X-Token: <examiner_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "index": 0,
    "status": "ok"
  }'
```

**Status-Optionen:**
- `"ok"` - Richtig beantwortet
- `"meh"` - Teilweise richtig
- `"fail"` - Falsch beantwortet

**Response (200 OK):**
```json
{
  "status": "graded"
}
```

**Errors:**
- `400` - Invalid status oder missing fields

---

## Health Check

### GET /health
Prüfe ob Backend läuft

**Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "No files provided"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing X-Token header"
}
```

### 403 Forbidden
```json
{
  "detail": "Invalid token or insufficient permissions for role: examiner"
}
```

### 404 Not Found
```json
{
  "detail": "Session not found"
}
```

---

## Session Workflow (Beispiel)

1. **Examiner erstellt Session:**
```bash
POST /session → {"session_id": "ABC12345", "examiner_token": "..."}
```

2. **Learner joined als Learner:**
```bash
POST /session/ABC12345/join {"role": "learner"} → {"token": "...", "role": "learner"}
```

3. **Examiner joined als Examiner (optional):**
```bash
POST /session/ABC12345/join {"role": "examiner"} → {"token": "...", "role": "examiner"}
```

4. **Learner lädt PDFs hoch:**
```bash
POST /session/ABC12345/upload [files] → {"status": "success", "uploaded": 2}
```

5. **Learner generiert Fragen:**
```bash
POST /session/ABC12345/generate {"pdf_texts": {...}} → {"question_count": 10}
```

6. **Learner pollt aktuelle Frage (alle 1s):**
```bash
GET /session/ABC12345/current → {"status": "locked", ...}
```

7. **Examiner holt alle Fragen:**
```bash
GET /session/ABC12345/questions → {"questions": [...], ...}
```

8. **Examiner gibt Frage frei:**
```bash
POST /session/ABC12345/reveal → {"status": "revealed"}
```

9. **Learner erhält Frage (nächster Poll):**
```bash
GET /session/ABC12345/current → {"status": "revealed", "question": "..."}
```

10. **Examiner bewertet:**
```bash
POST /session/ABC12345/grade {"index": 0, "status": "ok"} → {"status": "graded"}
```

11. **Examiner geht zur nächsten Frage:**
```bash
POST /session/ABC12345/next → {"status": "success"}
```

12. **Repeat 8-11 für alle Fragen**

---

## CORS Header

Backend sendet automatisch:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-Token
```

---

## Rate Limiting

Im MVP keine Rate Limits. In Production empfohlen:
- 10 Session-Creations pro Minute
- 5 Uploads pro Minute
- 100 Polls pro Minute

---

## Timestamps & Session Expiration

Sessions werden aktuell im RAM gespeichert. Keine automatische Expiration.

**Zukünftig (mit DB):**
- `created_at`: Timestamp der Session-Erstellung
- `expires_at`: Session läuft nach 24h ab
- Automatisches Cleanup von abgelaufenen Sessions

