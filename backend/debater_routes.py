"""Debater session management and COZE proxy — route handlers.

Session store and handlers are imported by app.py and registered
as @app.route() directly to avoid Blueprint vs catch-all routing issues.
"""

import uuid
import time
from flask import request, jsonify
from coze_client import chat_with_bot

# In-memory session store:  session_id -> dict
sessions = {}

MAX_SESSIONS = 50
MAX_MESSAGES_PER_SESSION = 100


def _clean_old_sessions():
    """Remove oldest sessions if over the limit."""
    if len(sessions) <= MAX_SESSIONS:
        return
    sorted_ids = sorted(
        sessions.keys(), key=lambda sid: sessions[sid]["updated_at"]
    )
    for sid in sorted_ids[: len(sessions) - MAX_SESSIONS]:
        del sessions[sid]


def handle_chat():
    """POST /api/chat

    Body: {
        api_key: str,
        bot_id: str,
        session_id: str,
        message: str,
        mode: "debate" | "discuss",
        api_url: str (optional) — COZE API base URL
    }
    Returns: {
        session_id: str,
        text: str,
        audio_url: str | null
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    api_key = data.get("api_key", "").strip()
    bot_id = data.get("bot_id", "").strip()
    session_id = data.get("session_id", "").strip()
    message = data.get("message", "").strip()
    mode = data.get("mode", "debate")
    api_url = data.get("api_url", "").strip() or None

    if not api_key:
        return jsonify({"error": "COZE API Key is required"}), 400
    if not bot_id:
        return jsonify({"error": "Bot ID is required"}), 400
    if not message:
        return jsonify({"error": "Message is required"}), 400
    if mode not in ("debate", "discuss"):
        return jsonify({"error": "Mode must be 'debate' or 'discuss'"}), 400

    # Ensure session exists — use the frontend's session_id
    if not session_id:
        session_id = str(uuid.uuid4())
    if session_id not in sessions:
        sessions[session_id] = {
            "mode": mode,
            "bot_id": bot_id,
            "conversation_id": None,
            "messages": [],
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        _clean_old_sessions()

    session = sessions[session_id]
    session["mode"] = mode
    session["updated_at"] = time.time()

    # Enforce per-session message cap
    if len(session["messages"]) >= MAX_MESSAGES_PER_SESSION:
        return jsonify(
            {"error": "Session message limit reached (100)"}
        ), 400

    # Call COZE
    try:
        result = chat_with_bot(
            api_key=api_key,
            bot_id=bot_id,
            user_message=message,
            conversation_id=session["conversation_id"],
            api_url=api_url,
        )
    except RuntimeError as e:
        msg = str(e)
        if "Invalid" in msg or "401" in msg or "403" in msg:
            return jsonify({"error": msg}), 401
        return jsonify({"error": msg}), 502

    # Store user message + AI response in session
    now = time.time()
    session["messages"].append({
        "role": "user",
        "content": message,
        "audio_url": None,
        "timestamp": now,
    })
    session["messages"].append({
        "role": "assistant",
        "content": result["text"],
        "audio_url": result.get("audio_url"),
        "timestamp": now,
    })
    session["updated_at"] = now

    # Update conversation_id for multi-turn continuity
    conv_id = result.get("conversation_id")
    if conv_id:
        session["conversation_id"] = conv_id

    return jsonify({
        "session_id": session_id,
        "text": result["text"],
        "audio_url": result.get("audio_url"),
    })


def list_sessions():
    """GET /api/sessions — return all sessions (metadata only)."""
    result = []
    sorted_sessions = sorted(
        sessions.items(),
        key=lambda kv: kv[1]["updated_at"],
        reverse=True,
    )
    for sid, s in sorted_sessions:
        preview = next(
            (
                m["content"][:60]
                for m in s["messages"]
                if m["role"] == "user"
            ),
            "New Chat",
        )
        result.append({
            "session_id": sid,
            "mode": s["mode"],
            "message_count": len(s["messages"]),
            "created_at": s["created_at"],
            "updated_at": s["updated_at"],
            "preview": preview,
        })
    return jsonify({"sessions": result})


def get_session(session_id):
    """GET /api/sessions/<id> — return full session including messages."""
    s = sessions.get(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({
        "session_id": session_id,
        "mode": s["mode"],
        "messages": s["messages"],
        "created_at": s["created_at"],
        "updated_at": s["updated_at"],
    })


def delete_session(session_id):
    """DELETE /api/sessions/<id> — remove a session."""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Session not found"}), 404
