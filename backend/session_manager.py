"""In-memory session store for debater/discussion conversations.

Manages session lifecycle: create, retrieve, update, delete.
The session store is a plain dict keyed by session_id — no persistence by
design (sessions live only as long as the server process).

Future: swap this dict for a SQLite/Redis backend without changing the API.
"""

import time
import uuid
from threading import Lock


MAX_SESSIONS = 50
MAX_MESSAGES_PER_SESSION = 100


class SessionManager:
    """Thread-safe in-memory session store.

    Usage:
        from session_manager import session_manager
        sid = session_manager.create(mode="debate", bot_id="bot_123")
        session = session_manager.get(sid)
        session_manager.add_messages(sid, [{"role": "user", "content": "Hi"}])
    """

    def __init__(self):
        self._sessions: dict = {}
        self._lock = Lock()

    # ── CRUD ────────────────────────────────────────────────────────

    def create(self, mode: str = "debate", bot_id: str = "") -> str:
        """Create a new session and return its ID."""
        sid = str(uuid.uuid4())
        now = time.time()
        with self._lock:
            self._sessions[sid] = {
                "mode": mode,
                "bot_id": bot_id,
                "conversation_id": None,
                "messages": [],
                "created_at": now,
                "updated_at": now,
            }
            self._trim()
        return sid

    def get(self, session_id: str) -> dict | None:
        """Return a session dict or None."""
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str, mode: str = "debate", bot_id: str = "") -> str:
        """Return existing session_id or create a new one.

        Returns the session_id (may differ from input if it didn't exist).
        """
        with self._lock:
            if session_id and session_id in self._sessions:
                return session_id
        return self.create(mode=mode, bot_id=bot_id)

    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True if it existed."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def list_all(self) -> list[dict]:
        """Return all sessions as a list of metadata dicts (no messages)."""
        with self._lock:
            items = sorted(
                self._sessions.items(),
                key=lambda kv: kv[1]["updated_at"],
                reverse=True,
            )
        result = []
        for sid, s in items:
            preview = "New Chat"
            for m in s["messages"]:
                if m["role"] == "user":
                    preview = m["content"][:60]
                    break
            result.append({
                "session_id": sid,
                "mode": s["mode"],
                "message_count": len(s["messages"]),
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "preview": preview,
            })
        return result

    def get_full(self, session_id: str) -> dict | None:
        """Return full session dict including messages, or None."""
        with self._lock:
            s = self._sessions.get(session_id)
            if not s:
                return None
            return {
                "session_id": session_id,
                "mode": s["mode"],
                "messages": list(s["messages"]),
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
            }

    # ── Messages ────────────────────────────────────────────────────

    def add_messages(self, session_id: str, messages: list[dict]) -> bool:
        """Append messages to a session. Returns False if session missing."""
        with self._lock:
            s = self._sessions.get(session_id)
            if not s:
                return False
            now = time.time()
            for msg in messages:
                msg.setdefault("timestamp", now)
            s["messages"].extend(messages)
            # Enforce per-session message cap
            if len(s["messages"]) > MAX_MESSAGES_PER_SESSION:
                s["messages"] = s["messages"][-MAX_MESSAGES_PER_SESSION:]
            s["updated_at"] = now
            return True

    def set_conversation_id(self, session_id: str, conversation_id: str) -> None:
        """Update the COZE conversation_id for multi-turn continuity."""
        with self._lock:
            s = self._sessions.get(session_id)
            if s:
                s["conversation_id"] = conversation_id
                s["updated_at"] = time.time()

    def get_conversation_id(self, session_id: str) -> str | None:
        """Return the stored COZE conversation_id or None."""
        with self._lock:
            s = self._sessions.get(session_id)
            return s["conversation_id"] if s else None

    def is_full(self, session_id: str) -> bool:
        """Check if a session has hit the message cap."""
        with self._lock:
            s = self._sessions.get(session_id)
            return len(s["messages"]) >= MAX_MESSAGES_PER_SESSION if s else False

    # ── Internal ────────────────────────────────────────────────────

    def _trim(self):
        """Remove oldest sessions if over the limit."""
        if len(self._sessions) <= MAX_SESSIONS:
            return
        sorted_ids = sorted(
            self._sessions.keys(),
            key=lambda sid: self._sessions[sid]["created_at"],
        )
        for sid in sorted_ids[: len(self._sessions) - MAX_SESSIONS]:
            del self._sessions[sid]


# Module-level singleton
session_manager = SessionManager()
