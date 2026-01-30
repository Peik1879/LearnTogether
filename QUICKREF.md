# StudyDuel - Quick Reference Card

## START (2 Terminals)

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## CORE FLOW (Step-by-Step)

1. **Create Session (Button: "Neue Session erstellen")**
   - Returns: `session_code` (8 Chars)
   - You get: `examiner_token`

2. **Learner Joins (Button: "Session beitreten")**
   - Enter: `session_code`
   - Select: "Als Learner beitreten"
   - Gets: `learner_token`

3. **Examiner Joins (Button: "Session beitreten")**
   - Enter: `session_code`
   - Select: "Als Examiner beitreten"
   - Gets: `examiner_token`

4. **Learner Uploads PDFs**
   - File picker: Select 1+ PDFs
   - Click: "Hochladen"
   - Backend: Extracts text, generates 10 questions

5. **Learner Sees Waiting Screen**
   - Shows: "Warte auf nächste Frage"
   - Polls: `/current` every 1s
   - Status: locked (question hidden)

6. **Examiner Sees Question List**
   - All 10 questions visible
   - Current: Question 1
   - Status: 🔒 Locked

7. **Examiner Reveals Question**
   - Click: "Frage freigeben (Reveal)"
   - Status: ✓ Revealed
   - Learner now sees question

8. **Examiner Grades Answer**
   - Choose: ✓ OK | ~ MEH | ✗ FAIL
   - Summary updates automatically

9. **Examiner Goes to Next**
   - Click: "Weiter zur nächsten Frage"
   - Back to step 7 for next question

10. **Repeat until all questions done**

---

## KEY FILES

### Backend
| File | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app + endpoints |
| `app/models.py` | SessionData, SessionStore |
| `app/services.py` | Business logic |
| `app/utils.py` | PDF parsing, tokens, questions |

### Frontend
| File | Purpose |
| --- | --- |
| `src/App.tsx` | Main component router |
| `src/pages/Landing.tsx` | Session create/join |
| `src/pages/LearnerPage.tsx` | Upload + poll |
| `src/pages/ExaminerPage.tsx` | Questions + controls |
| `src/services/api.ts` | API client |
| `src/styles/App.css` | Styling |

---

## API ENDPOINTS (Quick)

### No Auth Needed
- `POST /session` → returns `{session_id, examiner_token}`
- `POST /session/{id}/join` + `{role}` → returns `{token, role}`

### Auth with X-Token Header
| Endpoint | Method | Role | Purpose |
| --- | --- | --- | --- |
| `/session/{id}/upload` | POST | learner | Upload PDFs |
| `/session/{id}/generate` | POST | learner | Generate questions |
| `/session/{id}/current` | GET | learner | Get current question |
| `/session/{id}/questions` | GET | examiner | Get all questions |
| `/session/{id}/reveal` | POST | examiner | Reveal question |
| `/session/{id}/next` | POST | examiner | Next question |
| `/session/{id}/grade` | POST | examiner | Grade answer |

---

## SECURITY RULES

✓ Learner CANNOT see full question list  
✓ Learner CAN ONLY see current question (if revealed)  
✓ Learner CANNOT grade questions  
✓ Examiner CAN see all questions always  
✓ Examiner CANNOT upload PDFs  
✓ Token validation on every request  
✓ Role checking enforced server-side  

---

## DEBUGGING

### Backend doesn't start?
```bash
# Check Python version
python --version  # should be 3.8+

# Reinstall deps
pip install --force-reinstall -r requirements.txt

# Try different port
uvicorn app.main:app --port 9000
```

### Frontend doesn't start?
```bash
# Check Node version
node --version  # should be 14+

# Clear cache
rm -rf node_modules package-lock.json
npm install

# Try different port
npm run dev -- --port 5174
```

### CORS error in browser?
- Backend CORS allows `localhost:5173` ✓
- Make sure frontend is on 5173
- Check browser Network tab for exact URLs

### "Session not found"?
- Backend was restarted (sessions lost)
- Invalid session code
- Session code typo

### API returns 403?
- Wrong role (learner trying examiner endpoint)
- Invalid or missing X-Token
- Wrong token for role

---

## TEST IT FAST

### Python script
```bash
cd backend
python test_api.py
```

Runs 10 tests automatically, shows results.

### Manual cURL test
```bash
# Create session
curl -X POST http://localhost:8000/session

# Join as learner
curl -X POST http://localhost:8000/session/ABC12345/join \
  -H "Content-Type: application/json" \
  -d '{"role":"learner"}'

# Get current (as learner)
curl -X GET http://localhost:8000/session/ABC12345/current \
  -H "X-Token: <token>"
```

---

## PRODUCTION CHECKLIST

- [ ] Replace in-memory → PostgreSQL
- [ ] Add JWT expiration
- [ ] Implement user login/auth
- [ ] Add LLM for better questions
- [ ] Use WebSocket for real-time
- [ ] Add audit logging
- [ ] Set up monitoring
- [ ] Configure rate limits
- [ ] Add environment variables
- [ ] Deploy with Docker

---

## COMMON PATTERNS

### Poll question every 1s (JavaScript)
```javascript
const interval = setInterval(async () => {
  const response = await fetch(`/session/${id}/current`, {
    headers: { 'X-Token': token }
  });
  const data = await response.json();
  if (data.status === 'revealed') {
    console.log(data.question);
  }
}, 1000);
```

### Grade multiple questions (Python)
```python
for index, status in enumerate(['ok', 'meh', 'fail', 'ok']):
    requests.post(
        f"http://localhost:8000/session/{session_id}/grade",
        json={"index": index, "status": status},
        headers={"X-Token": token}
    )
```

### Extract text from PDF (Python)
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

---

## KEYBOARD SHORTCUTS

**Browser DevTools**
- F12: Open/close
- Ctrl+Shift+I: Inspect element
- Ctrl+Shift+N: New private window
- Tab: Switch tabs

**Terminal**
- Ctrl+C: Stop server
- Ctrl+L: Clear screen
- Up Arrow: Previous command

---

## HELP & SUPPORT

### Documentation
- `README.md` - Overview
- `TESTING.md` - Testing guide
- `API_REFERENCE.md` - Full API docs
- `ARCHITECTURE.md` - Design details
- `EXTENSIONS.md` - Future features

### Health Check
```bash
curl http://localhost:8000/health
```

### View All Sessions (Dev)
```python
from app.models import store
for id, session in store.sessions.items():
    print(f"{id}: {len(session.questions)} questions")
```

---

**Last Updated:** Jan 30, 2026  
**Version:** 1.0.0 MVP  
**Status:** Ready for Testing ✓
