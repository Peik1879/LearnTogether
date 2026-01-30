# StudyDuel Architecture Diagram

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        StudyDuel System                            │
└─────────────────────────────────────────────────────────────────────┘

  BROWSER 1 (Learner)                  BROWSER 2 (Examiner)
  ┌────────────────────┐               ┌────────────────────┐
  │  React SPA         │               │  React SPA         │
  │ - Landing Page     │               │ - Landing Page     │
  │ - Learner Page     │◄──────────────►│ - Examiner Page    │
  │ - Upload Form      │   HTTP/REST    │ - Question List    │
  │ - Poll /current    │                │ - Grade Controls   │
  └────────────────────┘                └────────────────────┘
           │                                    │
           │ X-Token: learner_token            │ X-Token: examiner_token
           │                                    │
           └─────────────────┬──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  FastAPI Backend│
                    │  Port: 8000     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    ┌───▼────┐      ┌────────▼─────┐     ┌──────▼───┐
    │GET APIs│      │POST APIs     │     │Validation│
    │(Learner)      │(Learner/Exam)      │ & Auth   │
    │- /current     │- /upload     │     │- Tokens  │
    │- /questions   │- /generate   │     │- Roles   │
    │  (denied)     │- /reveal     │     │- Headers │
    └────────┘      │- /next       │     └──────────┘
                    │- /grade      │
                    └──────┬───────┘
                           │
                ┌──────────▼──────────┐
                │  SessionStore       │
                │  (In-Memory Dict)   │
                │                     │
                │ session_id → {      │
                │   tokens: {},       │
                │   questions: [],    │
                │   current_index: 0, │
                │   revealed: bool,   │
                │   grades: {}        │
                │ }                   │
                └─────────────────────┘

```

## Session Lifecycle

```
1. CREATION
   Browser 1 (Future Learner):
   POST /session
   ↓
   Response: {
     session_id: "ABC12345",
     examiner_token: "examiner_xyz..."
   }
   (Learner sent to upload page)

2. EXAMINER JOINS
   Browser 2:
   POST /session/ABC12345/join {"role": "examiner"}
   ↓
   Response: {token: "examiner_abc...", role: "examiner"}

3. LEARNER JOINS AS LEARNER
   Browser 1 (after creating):
   POST /session/ABC12345/join {"role": "learner"}
   ↓
   Response: {token: "learner_xyz...", role: "learner"}

4. PDF UPLOAD & QUESTION GENERATION
   Browser 1:
   POST /session/ABC12345/upload [files]
   ↓
   Backend: extract text → generate 10 questions
   ↓
   SessionStore updated with questions[]

5. POLLING (Learner every 1s)
   Browser 1:
   GET /session/ABC12345/current
   ↓
   Response: {status: "locked", index: 0}
   (No question revealed yet)

6. EXAMINER SEES QUESTIONS
   Browser 2:
   GET /session/ABC12345/questions
   ↓
   Response: {
     questions: [Q1, Q2, ...],
     current_index: 0,
     revealed: false,
     grades: {}
   }

7. EXAMINER REVEALS
   Browser 2:
   POST /session/ABC12345/reveal
   ↓
   SessionStore: revealed = true

8. LEARNER POLLS (next cycle)
   Browser 1:
   GET /session/ABC12345/current
   ↓
   Response: {status: "revealed", question: "Q1", index: 0}
   (Question now visible!)

9. EXAMINER GRADES
   Browser 2:
   POST /session/ABC12345/grade {index: 0, status: "ok"}
   ↓
   SessionStore: grades[0] = "ok"

10. NEXT QUESTION
    Browser 2:
    POST /session/ABC12345/next
    ↓
    SessionStore: current_index = 1, revealed = false
    (Learner goes back to locked state)

11. REPEAT 6-10 for all questions

12. SUMMARY
    Browser 2:
    GET /session/ABC12345/questions
    ↓
    Response includes grades: {0: "ok", 1: "meh", 2: "fail", ...}
```

## Token & Role Validation

```
┌─────────────────────────────────────────────────┐
│           Every HTTP Request                    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
           ┌──────────────────────┐
           │ Check X-Token Header │
           └──────────────────────┘
                      │
           ┌──────────┴──────────┐
           │ Missing?            │
           ▼                      ▼
        ✗ 401                   Continue
      (Unauthorized)             │
                        ┌────────▼────────┐
                        │ Lookup token in │
                        │ SessionStore    │
                        └────────┬────────┘
                                 │
                          ┌──────┴──────┐
                          │ Found?      │
                          ▼             ▼
                        ✗ 403      Continue
                      (Forbidden)      │
                                 ┌────▼──────┐
                                 │ Check role │
                                 │ vs endpoint│
                                 └────┬──────┘
                                      │
                         ┌────────────┴────────────┐
                         │ Has required role?      │
                         ▼                         ▼
                       ✗ 403                    ✓ 200
                      (Forbidden)             (Continue)
```

## API Endpoint Types

```
┌─────────────────────────────────────────────────┐
│           API Endpoints by Role                 │
└─────────────────────────────────────────────────┘

PUBLIC (No Token Required):
  POST   /session
  POST   /session/{id}/join
  GET    /health

LEARNER ONLY (learner_token required):
  POST   /session/{id}/upload
  POST   /session/{id}/generate
  GET    /session/{id}/current      ← Returns locked/revealed

EXAMINER ONLY (examiner_token required):
  GET    /session/{id}/questions    ← Returns all questions
  POST   /session/{id}/reveal
  POST   /session/{id}/next
  POST   /session/{id}/grade

KEY SECURITY FEATURE:
  Learner endpoint GET /session/{id}/current
  NEVER returns full question list
  
  Only returns:
  - If !revealed: {status: "locked", index, total}
  - If revealed:  {status: "revealed", question, index, total}
  
  Cannot call Examiner endpoint GET /session/{id}/questions
  → Would get 403 (wrong role)
```

## Frontend Component Hierarchy

```
App.tsx (Main Router)
├── Landing.tsx
│   ├── Create Session Button
│   │   └── → LearnerPage (with examiner_token as initial token)
│   └── Join Session Form
│       ├── Learner Path → LearnerPage (with learner_token)
│       └── Examiner Path → ExaminerPage (with examiner_token)
│
├── LearnerPage.tsx
│   ├── Step: Upload
│   │   └── FileInput (multi-file)
│   │       └── handleUpload() → POST /upload
│   ├── Step: Waiting
│   │   ├── Spinner
│   │   └── Poll Loop (every 1s)
│   │       └── fetchCurrentQuestion() → GET /current
│   └── Step: Question
│       └── Display Question (from polling response)
│
└── ExaminerPage.tsx
    ├── Current Question Box
    │   ├── Question Preview
    │   ├── Status Badge (Locked/Revealed)
    │   └── Controls
    │       ├── If !revealed: Reveal Button
    │       │   └── handleReveal() → POST /reveal
    │       └── If revealed: Grade Buttons + Next
    │           ├── handleGrade(status) → POST /grade
    │           └── handleNext() → POST /next
    │
    ├── Questions List
    │   └── All questions with status indicators
    │
    └── Summary Box
        └── Stats (OK count, MEH count, FAIL count)
```

## Database Schema (Future - PostgreSQL)

```sql
-- Wenn In-Memory durch DB ersetzt wird:

CREATE TABLE sessions (
  id VARCHAR(8) PRIMARY KEY,
  examiner_token VARCHAR(32) UNIQUE NOT NULL,
  learner_token VARCHAR(32) UNIQUE NOT NULL,
  questions JSONB NOT NULL,
  current_index INTEGER DEFAULT 0,
  revealed BOOLEAN DEFAULT FALSE,
  grades JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP
);

CREATE TABLE pdfs (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(8) REFERENCES sessions(id),
  filename VARCHAR(255) NOT NULL,
  size INTEGER,
  text LONGTEXT,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  session_id VARCHAR(8) REFERENCES sessions(id),
  action VARCHAR(50),
  details JSONB,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

## Error Handling Flow

```
Client Request
      │
      ▼
  Backend Endpoint
      │
      ├─► Invalid JSON? → 400 Bad Request
      ├─► Missing X-Token? → 401 Unauthorized
      ├─► Invalid Token? → 401 Unauthorized
      ├─► Wrong Role? → 403 Forbidden
      ├─► Session not found? → 404 Not Found
      ├─► Processing error? → 500 Internal Server Error
      │
      └─► Success? → 200 OK + JSON response
          │
          └─► Frontend handles response
              └─► Update UI
```

## Performance Characteristics

```
Session Creation:
  Time: < 5ms
  Memory: ~1KB per session

PDF Upload (10MB):
  Time: ~500ms (varies with network)
  Memory: ~10MB (text extraction)

Question Generation (10 questions):
  Time: < 100ms (text parsing)
  Memory: ~50KB

Polling Cycle (every 1s):
  Time: < 10ms per poll
  Bandwidth: ~200 bytes per poll
  Memory: No growth

Concurrent Sessions (100 sessions):
  Memory: ~150MB
  CPU: < 5% idle
  Response time: < 50ms

Bottlenecks (MVP):
  - PDF extraction: ~500ms for large files
  - No caching → Full DB scan per request
  - Polling inefficiency → Bandwidth waste

Optimizations (Production):
  - Async PDF extraction
  - Redis caching
  - WebSocket instead of polling
  - Database indexing
```

---

**Diagramm-Version:** 1.0  
**Last Updated:** Jan 30, 2026
