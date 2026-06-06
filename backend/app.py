"""Flask API server for AI novel translation.

Supports both:
- Dev mode: Vite dev server proxies /api to Flask (port 5000)
- Production/EXE mode: Flask serves built frontend + API on same port
"""

import os
import sys
import time
import traceback
import mimetypes
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from translator import translate
from debater_routes import handle_chat, list_sessions, get_session, delete_session
from config import FLASK_PORT, FLASK_HOST, MAX_CONTENT_LENGTH
from config_manager import config_manager
from shutdown import register_shutdown_handlers, request_shutdown, is_shutting_down

# ── Path handling for PyInstaller ──────────────────────────────────────────
# When packaged with PyInstaller, sys._MEIPASS points to the temp
# extraction directory where bundled data files live.
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
HAS_STATIC = os.path.isdir(STATIC_DIR)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


# ── API Routes ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/api/config", methods=["GET"])
def api_get_config():
    """Return the current persistent configuration.

    Returns all config keys — the frontend decides which fields to display.
    """
    cfg = config_manager.get_config()
    return jsonify(cfg)


@app.route("/api/config", methods=["POST"])
def api_update_config():
    """Update persistent configuration.

    Body: a JSON object with the keys to update.
    Example: {"api_key": "pat_xxx", "bot_id_debate": "bot_yyy"}
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    # Only persist known keys (ignore unknown ones to avoid junk)
    safe = {}
    for key in config_manager.DEFAULTS:
        if key in data and isinstance(data[key], str):
            safe[key] = data[key].strip()

    if safe:
        config_manager.update_config(safe)

    return jsonify({"status": "ok", "updated": list(safe.keys())})


@app.route("/api/translate", methods=["POST"])
def handle_translate():
    """POST /api/translate
    Body: { api_key: str, novel_text: str, vocab_text: str }
    Returns: { translated_text: str, highlights: [{word, start, end}] }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    api_key = (data.get("api_key", "") or "").strip()
    novel_text = (data.get("novel_text", "") or "").strip()
    vocab_text = (data.get("vocab_text", "") or "").strip()

    # Validation
    if not api_key:
        return jsonify({"error": "API Key is required"}), 400
    if not novel_text:
        return jsonify({"error": "Novel text is required"}), 400

    # Parse vocabulary list (one word/phrase per line)
    vocab_list = []
    if vocab_text:
        vocab_list = [w.strip() for w in vocab_text.split("\n") if w.strip()]

    try:
        result = translate(api_key, novel_text, vocab_list)
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return jsonify({"error": "Invalid API Key. Please check your DeepSeek API key."}), 401
        if "402" in error_msg or "insufficient" in error_msg.lower():
            return jsonify({"error": "Insufficient balance. Please top up your DeepSeek account."}), 402
        return jsonify({"error": f"Translation failed: {error_msg}"}), 500


# ── Debater / COZE Chat Routes ─────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Proxy a chat message to COZE bot and return the response."""
    return handle_chat()


@app.route("/api/sessions", methods=["GET"])
def api_list_sessions():
    """Return all debater sessions (metadata only)."""
    return list_sessions()


@app.route("/api/sessions/<session_id>", methods=["GET"])
def api_get_session(session_id):
    """Return a single debater session with full message history."""
    return get_session(session_id)


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def api_delete_session(session_id):
    """Delete a debater session."""
    return delete_session(session_id)


# ── Frontend Static Serving (production / EXE mode) ────────────────────────

@app.route("/")
def serve_index():
    """Serve the frontend entry point."""
    if HAS_STATIC:
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"error": "Frontend not built. Run: cd frontend && npm run build"}), 404


@app.route("/<path:path>")
def serve_frontend(path):
    """Serve frontend assets with SPA fallback."""
    if HAS_STATIC:
        file_path = os.path.join(STATIC_DIR, path)
        if os.path.isfile(file_path):
            mimetype, _ = mimetypes.guess_type(file_path)
            return send_from_directory(STATIC_DIR, path, mimetype=mimetype)
        # SPA fallback — let React handle the route
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"error": "Not found"}), 404


# ── Shutdown endpoint (called by frontend on window unload) ───────────────

@app.route("/api/shutdown", methods=["POST"])
def api_shutdown():
    """Gracefully shut down the server from the frontend.

    In EXE mode, the frontend can call this on ``beforeunload`` so the
    Python process exits when the browser tab/window is closed.
    """
    # Only allow shutdown from localhost
    if request.remote_addr not in ("127.0.0.1", "::1", "localhost"):
        return jsonify({"error": "Forbidden"}), 403
    request_shutdown()
    return jsonify({"status": "shutting_down"})


# ── Startup ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import webbrowser

    # ── Register clean-exit handlers (must be first) ────────────
    register_shutdown_handlers()

    # Log where config is stored
    print(f"  Config: {config_manager.path}")

    def open_browser():
        """Auto-open the app in the default browser after a short delay."""
        url = f"http://{FLASK_HOST}:{FLASK_PORT}"
        print(f"  Opening {url} ...")
        webbrowser.open(url)

    print("=" * 56)
    print("  AI Novel Translator Server")
    print(f"  URL:  http://{FLASK_HOST}:{FLASK_PORT}")
    print("  Press Ctrl+C to stop the server")
    print("=" * 56)

    # Only auto-open when the frontend is bundled (production/EXE mode).
    if HAS_STATIC:
        threading.Timer(1.0, open_browser).start()

    # ── Run Flask with periodic shutdown check ──────────────────
    # In EXE mode we check the shutdown event periodically so the
    # process doesn't hang after the user closes the browser.
    if getattr(sys, "frozen", False):
        # Run Flask in a daemon thread so the main thread can watch for exit.
        flask_thread = threading.Thread(
            target=lambda: app.run(
                debug=False,
                host=FLASK_HOST,
                port=FLASK_PORT,
                use_reloader=False,
            ),
            daemon=True,
        )
        flask_thread.start()

        # Main thread: wait for shutdown signal.
        try:
            while not is_shutting_down():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            request_shutdown()
            print("\n  Exiting...", file=sys.stderr)
            # Give the Flask thread a moment to finish requests.
            flask_thread.join(timeout=3)
            sys.exit(0)
    else:
        # Dev mode: run Flask normally (Ctrl+C to stop).
        try:
            app.run(
                debug=False,
                host=FLASK_HOST,
                port=FLASK_PORT,
                use_reloader=False,
            )
        except KeyboardInterrupt:
            pass
