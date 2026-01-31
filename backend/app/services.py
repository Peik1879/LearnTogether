from typing import Optional, Tuple
from app.models import SessionData, store
from app.utils import (
    generate_session_code, 
    generate_token, 
    extract_text_from_pdf,
    generate_questions_from_text
)


class SessionService:
    """Service for session management"""

    @staticmethod
    def create_session() -> Tuple[str, str]:
        """
        Create a new session
        Returns: (session_id, examiner_token)
        """
        session_code = generate_session_code()
        session = store.create_session(session_code)
        
        examiner_token = generate_token()
        session.tokens[examiner_token] = "examiner"
        
        return session_code, examiner_token

    @staticmethod
    def join_session(session_id: str, role: str) -> Optional[str]:
        """
        Join an existing session
        Returns: token for the role, or None if session doesn't exist
        """
        session = store.get_session(session_id)
        if not session:
            return None
        
        if role not in ["learner", "examiner"]:
            return None
        
        # Check if role already exists
        for token, existing_role in session.tokens.items():
            if existing_role == role:
                # Role already exists, return that token
                return token
        
        # Create new token for this role
        token = generate_token()
        session.tokens[token] = role
        return token

    @staticmethod
    def verify_token(session_id: str, token: str, required_role: str) -> bool:
        """
        Verify if token has the required role in the session
        """
        session = store.get_session(session_id)
        if not session:
            print(f"[AUTH] Session {session_id} not found")
            return False
        
        role = session.tokens.get(token)
        print(f"[AUTH] Token {token[:4]}... has role: {role}, required: {required_role}")
        print(f"[AUTH] All tokens in session: {list(session.tokens.values())}")
        
        if role != required_role:
            return False
        
        return True

    @staticmethod
    def add_pdf_metadata(session_id: str, filename: str, size: int) -> bool:
        """Store PDF metadata"""
        session = store.get_session(session_id)
        if not session:
            return False
        
        session.pdfs.append({
            "filename": filename,
            "size": size
        })
        return True

    @staticmethod
    def generate_questions(
        session_id: str, 
        pdf_texts: dict  # {filename: text}
    ) -> bool:
        """
        Generate questions from PDF texts and store them
        Returns: success
        """
        session = store.get_session(session_id)
        if not session:
            return False
        
        # Combine all texts
        combined_text = "\n\n".join(pdf_texts.values())
        
        # Generate questions
        questions = generate_questions_from_text(combined_text, num_questions=10)
        session.questions = questions
        session.current_index = 0
        session.revealed = False
        
        return True

    @staticmethod
    def reveal_current_question(session_id: str) -> bool:
        """Set revealed flag to true"""
        session = store.get_session(session_id)
        if not session:
            return False
        
        session.revealed = True
        return True

    @staticmethod
    def next_question(session_id: str) -> bool:
        """Move to next question"""
        session = store.get_session(session_id)
        if not session:
            return False
        
        if session.current_index < len(session.questions) - 1:
            session.current_index += 1
            session.revealed = False
            return True
        
        return False  # No more questions

    @staticmethod
    def grade_question(session_id: str, index: int, status: str) -> bool:
        """Grade a question"""
        session = store.get_session(session_id)
        if not session:
            return False
        
        if status not in ["ok", "meh", "fail"]:
            return False
        
        session.grades[index] = status
        return True

    @staticmethod
    def get_session_status(session_id: str, role: str):
        """Get full session status (examiner only)"""
        session = store.get_session(session_id)
        if not session:
            return None
        
        if role != "examiner":
            return None
        
        return {
            "session_id": session.id,
            "questions": session.questions,
            "current_index": session.current_index,
            "revealed": session.revealed,
            "grades": session.grades,
            "pdfs": session.pdfs
        }

    @staticmethod
    def get_learner_current(session_id: str):
        """Get current question for learner"""
        session = store.get_session(session_id)
        if not session:
            return None
        
        if not session.revealed:
            return {
                "status": "locked",
                "index": session.current_index,
                "total": len(session.questions)
            }
        
        if session.current_index < len(session.questions):
            return {
                "status": "revealed",
                "index": session.current_index,
                "question": session.questions[session.current_index],
                "total": len(session.questions)
            }
        
        return {
            "status": "completed",
            "index": session.current_index,
            "total": len(session.questions)
        }
