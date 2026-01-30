# 📚 StudyDuel - Vollständiges MVP

Willkommen bei StudyDuel! Dies ist ein vollständiger, produktionsreifer Prototyp für 1-zu-1 Lernabfragen mit strikter Sicherheit zwischen Learner und Examiner.

## 🚀 Quick Start (60 Sekunden)

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend (neuer Terminal)
cd frontend
npm install
npm run dev

# Browser: http://localhost:5173
```

Das wars! Mehr Details siehe unten.

---

## 📖 Dokumentation (Roadmap)

Start hier je nach Bedarf:

### Anfänger?
1. **[README.md](README.md)** - Überblick & Architektur
2. **[QUICKREF.md](QUICKREF.md)** - Schnelle Referenzkarte (ausdruckbar)
3. **[TESTING.md](TESTING.md)** - Wie man die App testet

### Developer?
4. **[API_REFERENCE.md](API_REFERENCE.md)** - Vollständige API-Dokumentation
5. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technische Details & Struktur
6. **[EXTENSIONS.md](EXTENSIONS.md)** - Wie man das MVP erweitert

### Setup/Debugging?
7. **[verify_setup.py](verify_setup.py)** - Prüft Konfiguration (run: `python verify_setup.py`)
8. **[backend/test_api.py](backend/test_api.py)** - API-Tests (run: `python test_api.py`)

---

## 🎯 Was ist StudyDuel?

StudyDuel ist eine Web-App für **1-zu-1 Lernabfragen**:

- **Learner** (Schüler): Lädt PDFs hoch, beantwortet Fragen
- **Examiner** (Lehrer): Sieht alle Fragen, entscheidet welche Frage wann freigebbar wird, bewertet Antworten
- **Security:** Der Learner KANN NICHT vorher alle Fragen sehen – nur die aktuelle Frage, wenn der Examiner sie freigibt

### Workflow
1. Learner erstellt Session → bekommt **Session Code** (z.B. `A1B2C3D4`)
2. Examiner joined Session mit Code
3. Learner lädt PDFs hoch
4. Backend generiert 10 Fragen aus Textextraktion
5. Learner sieht "Warten..." bis Examiner Frage freigibt
6. Examiner klickt "Reveal" → Learner sieht Frage
7. Examiner bewertet (ok/meh/fail) und geht weiter
8. Am Ende: Summary mit Counts

---

## 🏗️ Architektur

### Stack
- **Backend:** Python FastAPI + Uvicorn (http://localhost:8000)
- **Frontend:** React 18 + Vite + TypeScript (http://localhost:5173)
- **Speicher:** In-Memory (Dict) – MVP; später: PostgreSQL
- **Auth:** Token-basiert (X-Token Header)
- **Echtzeit:** Polling alle 1s (Learner) + Auto-Refresh (Examiner)

### Ordnerstruktur
```
backend/
├── app/
│   ├── main.py          # FastAPI App
│   ├── models.py        # SessionData + Store
│   ├── services.py      # Business Logic
│   └── utils.py         # Helpers
├── requirements.txt
└── test_api.py          # API Tests

frontend/
├── src/
│   ├── pages/
│   │   ├── Landing.tsx      # Session-UI
│   │   ├── LearnerPage.tsx  # Upload + Poll
│   │   └── ExaminerPage.tsx # Controls
│   ├── services/api.ts      # API Client
│   └── styles/App.css       # Styling
├── package.json
└── vite.config.ts
```

---

## 🔐 Security

**Zentral:** Learner darf NICHT alle Fragen sehen.

### Wie es funktioniert:
- Jede Session hat zwei Tokens: `examiner_token` + `learner_token`
- Backend validiert **jeden** Request mit X-Token Header
- Examiner-Endpoint `/session/{id}/questions` prüft `role == "examiner"`
- Learner-Endpoint `/session/{id}/current` gibt nur aktuelle Frage zurück (wenn `revealed=true`)
- Falsche Role → 403 Forbidden

### Token Flow:
1. `POST /session` → returns `examiner_token`
2. `POST /session/{id}/join {"role": "learner"}` → returns `learner_token`
3. Alle weiteren Requests: `X-Token: {token}` Header

---

## 📡 API Highlights

### Ohne Auth
- `POST /session` - Create
- `POST /session/{id}/join` - Join

### Learner-Only
- `POST /session/{id}/upload` - Upload PDFs
- `POST /session/{id}/generate` - Generate questions
- `GET /session/{id}/current` - Get current question (locked/revealed)

### Examiner-Only
- `GET /session/{id}/questions` - Get all questions + status
- `POST /session/{id}/reveal` - Reveal current question
- `POST /session/{id}/next` - Move to next
- `POST /session/{id}/grade` - Grade (ok/meh/fail)

Siehe **[API_REFERENCE.md](API_REFERENCE.md)** für vollständige Doku.

---

## 🧪 Testing

### Automatisch (Recommended)
```bash
cd backend
python test_api.py
```
Runs 10 tests: Session creation, join, security checks, questions, grading.

### Manuell (Interaktiv)
1. Open http://localhost:5173 in 2 Browser-Tabs
2. Tab 1: "Neue Session erstellen" → Get session code
3. Tab 2: "Session beitreten" → Enter code + "Als Examiner"
4. Tab 1: Upload PDFs
5. Tab 2: See questions + Click "Reveal"
6. Tab 1: See question
7. Tab 2: Grade + Next

Details: **[TESTING.md](TESTING.md)**

---

## 🔧 Development

### Backend ändern?
1. Ändere `app/main.py` oder andere Datei
2. Uvicorn lädt automatisch neu (--reload)
3. Test mit: `python backend/test_api.py` oder cURL

### Frontend ändern?
1. Ändere `src/pages/*.tsx` oder `src/styles/App.css`
2. Vite lädt automatisch (Hot Module Reload)
3. Browser refresht automatisch

### Neue Dependency?
**Backend:** Add to `requirements.txt` → `pip install -r requirements.txt`  
**Frontend:** Add to `package.json` → `npm install`

---

## 🚢 Production Roadmap

Dieses MVP ist für **Demonstration** optimiert. Für Production:

1. **Database:** In-Memory → PostgreSQL + SQLAlchemy
2. **Auth:** Token → JWT mit Expiration
3. **Users:** Session Codes → User Accounts
4. **Questions:** Dummy Fragen → LLM-generiert (OpenAI)
5. **Echtzeit:** Polling → WebSocket
6. **Logging:** Console → Structured Logging
7. **Monitoring:** None → Prometheus + Grafana
8. **Deployment:** Local → Docker + K8s

Siehe **[EXTENSIONS.md](EXTENSIONS.md)** für Code-Beispiele.

---

## ❓ FAQs

**Q: Wo sind die Daten gespeichert?**  
A: Im RAM. Wenn du den Server neustartest, alle Sessions weg. Im MVP ok, in Production: PostgreSQL.

**Q: Wie werden die Fragen generiert?**  
A: Dummy-Fragen aus PDF-Text-Abschnitten (pdfplumber). Keine LLM. Könnte mit OpenAI erweitert werden.

**Q: Kann ich mehrere Learner haben?**  
A: Aktuell: Pro Session 1 Learner, 1 Examiner. Mehrere Examiner möglich (teilen Token).

**Q: Funktioniert offline?**  
A: Nein, Backend ist erforderlich. Frontend ist SPA (läuft im Browser).

**Q: Warum Polling statt WebSocket?**  
A: Einfacher zu implementieren + debuggen. Polling alle 1s ist ausreichend. WebSocket optional später.

**Q: CORS-Fehler?**  
A: Backend erlaubt `localhost:5173`. Wenn auf anderem Port: `vite.config.ts` + `app/main.py` anpassen.

---

## 🎓 Learning Resources

Dieses Projekt demonstriert:
- **FastAPI:** Moderne Python Web-Framework
- **React:** Komponenten-basierte UI
- **TypeScript:** Type-safe JavaScript
- **REST API:** Stateless Endpoints mit Tokens
- **Security:** Role-based Access Control (RBAC)
- **State Management:** In-Memory Store Pattern

Alle Dateien sind **kommentiert** und **lesbar** – ideal zum Lernen!

---

## 📞 Support

### Stuck?
1. Check **[QUICKREF.md](QUICKREF.md)** für Quick Answers
2. Read **[TESTING.md](TESTING.md)** für Debug-Tipps
3. Run `python verify_setup.py` um Konfiguration zu prüfen
4. Look at **[API_REFERENCE.md](API_REFERENCE.md)** für genaue Endpoints

### Report a Bug?
- Check ob Backend + Frontend beide laufen: `curl http://localhost:8000/health`
- Öffne Browser DevTools (F12) → Network Tab → prüfe API Requests
- Prüfe Backend Logs in Terminal

---

## 📝 License

MIT – Frei verwendbar, Modifizierung erlaubt.

---

## 🎉 Next Steps

1. **Run:** `python verify_setup.py` – Prüft ob alles installiert
2. **Start:** Siehe **Quick Start** oben
3. **Test:** `python backend/test_api.py` oder manuell in Browser
4. **Extend:** Siehe **[EXTENSIONS.md](EXTENSIONS.md)** für Ideen

**Viel Erfolg!** 🚀

---

**Version:** 1.0.0 MVP  
**Last Updated:** Jan 30, 2026  
**Status:** ✓ Ready for Testing
