from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import tempfile
import os

from app.models import store
from app.services import SessionService
from app.utils import extract_text_from_pdf

app = FastAPI(title="StudyDuel API")

# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGINS", "")
cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5174",
]
if cors_origins_env:
    additional_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
    cors_origins.extend(additional_origins)

# Debug: Print CORS origins on startup
print(f"[CORS] Configured origins: {cors_origins}")
print(f"[CORS] Environment variable CORS_ORIGINS: {cors_origins_env or 'NOT SET'}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency for token verification
def verify_token(
    session_id: str,
    required_role: str,
    x_token: Optional[str] = Header(None)
):
    if not x_token:
        raise HTTPException(status_code=401, detail="Missing X-Token header")
    
    if not SessionService.verify_token(session_id, x_token, required_role):
        raise HTTPException(status_code=403, detail=f"Invalid token or insufficient permissions for role: {required_role}")
    
    return x_token


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.post("/session")
def create_session():
    """Create a new session, returns examiner_token"""
    session_id, examiner_token = SessionService.create_session()
    return {
        "session_id": session_id,
        "examiner_token": examiner_token
    }


@app.post("/session/{session_id}/join")
def join_session(session_id: str, body: dict):
    """
    Join an existing session
    Body: { "role": "learner" | "examiner" }
    Returns: { "token": "..." }
    """
    # Validate session exists
    if not store.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    role = body.get("role")
    if role not in ["learner", "examiner"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    token = SessionService.join_session(session_id, role)
    if not token:
        raise HTTPException(status_code=400, detail="Could not join session")
    
    return {
        "token": token,
        "role": role
    }


# ============================================================================
# Learner Endpoints
# ============================================================================

@app.post("/session/{session_id}/upload")
async def upload_pdfs(
    session_id: str,
    files: List[UploadFile] = File(...),
    x_token: Optional[str] = Header(None)
):
    """
    Upload PDFs for learning material
    Examiner only (the creator uploads the study material)
    """
    verify_token(session_id, "examiner", x_token)
    
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    pdf_texts = {}
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
        
        content = await file.read()
        SessionService.add_pdf_metadata(session_id, file.filename, len(content))
        pdf_texts[file.filename] = extract_text_from_pdf(content)

    # Auto-generate questions after upload
    SessionService.generate_questions(session_id, pdf_texts)
    
    return {
        "status": "success",
        "uploaded": len(files),
        "files": [f.filename for f in files]
    }


@app.post("/session/{session_id}/generate")
def generate_questions(
    session_id: str,
    body: dict,
    x_token: Optional[str] = Header(None)
):
    """
    Generate questions from uploaded PDFs
    Learner only
    Body: { "pdf_texts": { "filename": "text content", ... } }
    """
    verify_token(session_id, "learner", x_token)
    session = store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    pdf_texts = body.get("pdf_texts", {})
    
    if not pdf_texts:
        raise HTTPException(status_code=400, detail="No PDF texts provided")
    
    success = SessionService.generate_questions(session_id, pdf_texts)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to generate questions")
    
    return {
        "status": "success",
        "question_count": len(session.questions)
    }


@app.get("/session/{session_id}/current")
def get_current_question(
    session_id: str,
    x_token: Optional[str] = Header(None)
):
    """
    Get current question for learner
    Learner only
    Returns locked state if not revealed, or the actual question if revealed
    """
    verify_token(session_id, "learner", x_token)
    result = SessionService.get_learner_current(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return result


# ============================================================================
# Examiner Endpoints
# ============================================================================

@app.get("/session/{session_id}/questions")
def get_all_questions(
    session_id: str,
    x_token: Optional[str] = Header(None)
):
    """
    Get all questions for examiner
    Examiner only - returns full question list with metadata
    """
    verify_token(session_id, "examiner", x_token)
    result = SessionService.get_session_status(session_id, "examiner")
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return result


@app.post("/session/{session_id}/reveal")
def reveal_current_question(
    session_id: str,
    x_token: Optional[str] = Header(None)
):
    """
    Reveal current question to learner
    Examiner only
    """
    verify_token(session_id, "examiner", x_token)
    success = SessionService.reveal_current_question(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "revealed"}


@app.post("/session/{session_id}/next")
def next_question(
    session_id: str,
    x_token: Optional[str] = Header(None)
):
    """
    Move to next question
    Examiner only
    """
    verify_token(session_id, "examiner", x_token)
    success = SessionService.next_question(session_id)
    if not success:
        raise HTTPException(status_code=400, detail="No more questions or session not found")
    
    return {"status": "success"}


@app.post("/session/{session_id}/grade")
def grade_question(
    session_id: str,
    body: dict,
    x_token: Optional[str] = Header(None)
):
    """
    Grade a question
    Examiner only
    Body: { "index": int, "status": "ok" | "meh" | "fail" }
    """
    verify_token(session_id, "examiner", x_token)
    index = body.get("index")
    status = body.get("status")
    
    if index is None or status is None:
        raise HTTPException(status_code=400, detail="Missing index or status")
    
    success = SessionService.grade_question(session_id, index, status)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid grade status")
    
    return {"status": "graded"}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "LearnTogether API is running", "cors_origins": cors_origins}

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
