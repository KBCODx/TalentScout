from typing import Dict, Any, Optional
from app.models.schemas import Candidate

class SessionService:
    def __init__(self):
        # In-memory session storage: sessionId -> session_data
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def create_session(self, session_id: str, candidate: Candidate):
        self._sessions[session_id] = {
            "candidate": candidate,
            "history": [],
            "turn_count": 0,
            "status": "started"
        }
        return self._sessions[session_id]

    def update_session(self, session_id: str, message: str, reply: str):
        if session_id in self._sessions:
            self._sessions[session_id]["history"].append({"user": message, "bot": reply})
            self._sessions[session_id]["turn_count"] += 1

    def end_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id]["status"] = "completed"

# Global instance
session_manager = SessionService()
