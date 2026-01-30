from typing import Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionData:
    """In-memory session storage"""
    id: str
    tokens: Dict[str, str] = field(default_factory=dict)  # token -> role
    pdfs: List[Dict] = field(default_factory=list)  # [{filename, size}]
    questions: List[str] = field(default_factory=list)
    current_index: int = 0
    revealed: bool = False
    grades: Dict[int, str] = field(default_factory=dict)  # index -> "ok"|"meh"|"fail"
    created_at: datetime = field(default_factory=datetime.now)


class SessionStore:
    """Global session store (in-memory)"""
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}

    def create_session(self, session_id: str) -> SessionData:
        session = SessionData(id=session_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global store
store = SessionStore()
