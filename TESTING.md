# StudyDuel - Testing Guide

Diese Anleitung zeigt, wie die Applikation getestet wird.

## Quick Start (5 Minuten)

### Terminal 1: Backend starten

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Erwartet: `Uvicorn running on http://127.0.0.1:8000`

### Terminal 2: Frontend starten

```bash
cd frontend
npm install
npm run dev
```

Erwartet: `VITE v5.0.0 ready in xxx ms` und `Local: http://localhost:5173/`

### Browser 1 (Examiner)

1. Öffne `http://localhost:5173`
2. Klicke "Neue Session erstellen"
3. Du wirst zur Learner-Seite weitergeleitet (da du die Session erstellt hast)
4. Notiere dir den **Session Code** oben (z.B. `A1B2C3D4`)

### Browser 2 (Learner)

1. Öffne `http://localhost:5173` in neuem Fenster/Tab
2. Klicke "Session beitreten"
3. Gib Session Code ein
4. Wähle "Als Examiner beitreten"

Jetzt hast du zwei Browser-Fenster: Learner und Examiner.

## Test-Szenario: Vollständiger Durchlauf

### Schritt 1: Learner lädt PDFs hoch

Im **Learner-Fenster**:
1. Klicke "PDFs auswählen"
2. Laden Sie beliebige PDF-Dateien hoch (z.B. von der Festplatte)
3. Klicke "Hochladen"
4. Warte bis "Warten auf nächste Frage..." angezeigt wird

Erwartet: Keine Fragen für Learner sichtbar.

### Schritt 2: Examiner sieht Fragen

Im **Examiner-Fenster**:
1. Sollte automatisch die Fragenliste zeigen
2. Du sieht: "Aktuelle Frage", "Fragenliste", "Zusammenfassung"
3. Status: 🔒 Gesperrt

Erwartet: ~10 Fragen sind aufgelistet.

### Schritt 3: Examiner gibt Frage frei

Im **Examiner-Fenster**:
1. Klicke "Frage freigeben (Reveal)"
2. Status ändert sich auf ✓ Freigegeben
3. Buttons erscheinen: ✓ OK, ~ MEH, ✗ FAIL

Im **Learner-Fenster**:
- Die Frage erscheint!
- Learner sieht nun: "Frage 1 von 10" + die Frage

Erwartet: Text etwa "Erkläre: [inhalt]" oder "Was bedeutet: [inhalt]?"

### Schritt 4: Examiner bewertet

Im **Examiner-Fenster**:
1. Klicke eine Bewertung, z.B. "✓ OK"
2. Buttons verschwinden, "Weiter zur nächsten Frage" wird aktiv

Im **Learner-Fenster**:
- Noch kein Change (wartet auf nächste Frage)

Erwartet: Summary zeigt "OK: 1"

### Schritt 5: Nächste Frage

Im **Examiner-Fenster**:
1. Klicke "Weiter zur nächsten Frage"
2. Neue Frage wird angezeigt
3. Status: 🔒 Gesperrt

In **Learner-Fenster**:
- Zeigt wieder "Warten auf nächste Frage..." oder "Frage 2 von 10"

Erwartet: `current_index` ist jetzt 1

### Schritt 6: Wiederhole für alle Fragen

Wiederhole Schritte 3-5 für einige weitere Fragen. Verwende verschiedene Bewertungen.

Erwartet: Summary zeigt verschiedene Counts (OK, MEH, FAIL)

## Sicherheits-Tests

### Test 1: Learner kann Fragenliste NICHT sehen

Im **Learner-Fenster**, öffne Browser-Konsole (F12):

```javascript
const sessionId = "A1B2C3D4";  // Deine Session ID
const learnerToken = localStorage.getItem("learnerToken");  // Falls gespeichert

// Oder manuell: kopiere Token aus dem Network Tab

// Versuche, alle Fragen abzurufen:
fetch("http://localhost:8000/session/" + sessionId + "/questions", {
  headers: { "X-Token": learnerToken }
})
.then(r => r.json())
.then(console.log)
```

Erwartet: `"403 Invalid token or insufficient permissions for role: examiner"`

### Test 2: Examiner kann ohne Token NICHT zugreifen

```javascript
// Ohne X-Token Header
fetch("http://localhost:8000/session/A1B2C3D4/questions")
.then(r => r.json())
.then(console.log)
```

Erwartet: `"401 Missing X-Token header"`

### Test 3: Ungültige Session

```javascript
fetch("http://localhost:8000/session/INVALID123/questions", {
  headers: { "X-Token": "any-token" }
})
.then(r => r.json())
.then(console.log)
```

Erwartet: `"404 Session not found"`

## Fehler-Szenarien

### Szenario: Learner versucht zu graden

Im **Learner-Fenster**, Browser-Konsole:

```javascript
const learnerToken = "...";
fetch("http://localhost:8000/session/A1B2C3D4/grade", {
  method: "POST",
  headers: {
    "X-Token": learnerToken,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ index: 0, status: "ok" })
})
.then(r => r.json())
.then(console.log)
```

Erwartet: `"403 Invalid token or insufficient permissions for role: examiner"`

### Szenario: Doppelter Join als Learner

1. Browser 1: Joine Session als Learner
2. Browser 2: Joine GLEICHE Session als Learner

Erwartet: Beide bekommen den **gleichen Token** (System erkennt, dass Learner-Role bereits existiert)

## API-Tests mit cURL

### Session erstellen

```bash
curl -X POST http://localhost:8000/session
```

Response:
```json
{
  "session_id": "ABC12345",
  "examiner_token": "xyz..."
}
```

### Learner joinen

```bash
curl -X POST http://localhost:8000/session/ABC12345/join \
  -H "Content-Type: application/json" \
  -d '{"role": "learner"}'
```

Response:
```json
{
  "token": "learner_token_123",
  "role": "learner"
}
```

### Fragen abrufen (Examiner only)

```bash
curl -X GET http://localhost:8000/session/ABC12345/questions \
  -H "X-Token: <examiner_token>"
```

### Frage freigeben

```bash
curl -X POST http://localhost:8000/session/ABC12345/reveal \
  -H "X-Token: <examiner_token>"
```

## Performance-Tests (Optional)

### 100 Sessions gleichzeitig erstellen

```bash
for i in {1..100}; do
  curl -X POST http://localhost:8000/session
done
```

Erwartet: Alle erfolgreich (keine Performance-Degradation, da In-Memory)

### RAM-Verbrauch

Öffne `top` (Linux/Mac) oder Task Manager (Windows).

Im Normal-Betrieb: ~50-100 MB  
Mit 100 Sessions: ~150-200 MB

## Debugging

### Backend-Logs

Der Output von Uvicorn zeigt alle Requests:

```
INFO:     127.0.0.1:52345 - "POST /session HTTP/1.1" 200 OK
INFO:     127.0.0.1:52346 - "POST /session/ABC12345/join HTTP/1.1" 200 OK
```

### Frontend-Logs

Browser-Konsole (F12) zeigt API-Requests und Fehler.

### Session-Daten inspizieren

Backend-Python-Shell:

```python
from app.models import store

# Alle Sessions anschauen
for session_id, session in store.sessions.items():
    print(f"Session: {session_id}")
    print(f"  Questions: {len(session.questions)}")
    print(f"  Current Index: {session.current_index}")
    print(f"  Revealed: {session.revealed}")
    print(f"  Grades: {session.grades}")
```

## Häufige Probleme

**Problem:** CORS-Fehler im Browser  
**Lösung:** Backend läuft auf Port 8000, Frontend auf 5173. Prüfe `app/main.py` - CORS sollte beide erlauben.

**Problem:** "No module named 'pdfplumber'"  
**Lösung:** `pip install -r requirements.txt` im backend/ Ordner durchführen.

**Problem:** "Cannot find module 'react'"  
**Lösung:** `npm install` im frontend/ Ordner durchführen.

**Problem:** Frontend zeigt "Session not found"  
**Lösung:** Prüfe, dass Backend läuft (`http://localhost:8000/health` sollte 200 OK sein)

Viel Spaß beim Testen!
