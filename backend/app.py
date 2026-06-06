"""Flask API server — AI Novel Translator + Debater.

Supports:
- Dev mode:  Vite dev server proxies /api to Flask (port 5000)
- EXE mode:  Flask serves built frontend + API on the same port

Architecture (modular):
  routers/chat_router      — COZE chat + session endpoints
  routers/translate_router — DeepSeek translation endpoint
  routers/config_router    — persistent config read/write + status
  config_manager           — thread-safe config.json persistence
  session_manager          — in-memory session store
  shutdown                 — graceful exit handlers
  coze_client              — COZE v3 async API wrapper
"""

import os
import sys
import time
import mimetypes
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config import FLASK_PORT, FLASK_HOST, MAX_CONTENT_LENGTH
from config_manager import config_manager
from shutdown import register_shutdown_handlers, request_shutdown, is_shutting_down


def create_app() -> Flask:
    """Build and configure the Flask application."""
    # ── Paths (PyInstaller-aware) ──────────────────────────────
    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    static_dir = os.path.join(base_dir, "static")
    has_static = os.path.isdir(static_dir)

    # ── App ────────────────────────────────────────────────────
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    # ── Register modular route groups ───────────────────────────
    from routers.chat_router import register_chat_routes
    from routers.translate_router import register_translate_routes
    from routers.config_router import register_config_routes

    register_chat_routes(app)
    register_translate_routes(app)
    register_config_routes(app)

    # ── Health check ────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    # ── Shutdown (EXE mode) ────────────────────────────────────
    @app.route("/api/shutdown", methods=["POST"])
    def api_shutdown():
        if request.remote_addr not in ("127.0.0.1", "::1", "localhost"):
            return jsonify({"error": "Forbidden"}), 403
        request_shutdown()
        return jsonify({"status": "shutting_down"})

    # ── Frontend static serving (production / EXE mode) ─────────
    @app.route("/")
    def serve_index():
        if has_static:
            return send_from_directory(static_dir, "index.html")
        return jsonify({"error": "Frontend not built."}), 404

    @app.route("/<path:path>")
    def serve_frontend(path):
        if has_static:
            file_path = os.path.join(static_dir, path)
            if os.path.isfile(file_path):
                mimetype, _ = mimetypes.guess_type(file_path)
                return send_from_directory(static_dir, path, mimetype=mimetype)
            return send_from_directory(static_dir, "index.html")
        return jsonify({"error": "Not found"}), 404

    # Attach state for the startup block below
    app._has_static = has_static
    app._static_dir = static_dir
    return app


# ── Startup ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import webbrowser

    register_shutdown_handlers()

    app = create_app()
    has_static = app._has_static

    print(f"  Config: {config_manager.path}")
    print(f"  Static: {'present' if has_static else 'missing — dev mode'}")
    print("=" * 56)
    print("  AI Novel Translator Server")
    print(f"  URL:  http://{FLASK_HOST}:{FLASK_PORT}")
    print("  Press Ctrl+C to stop the server")
    print("=" * 56)

    if has_static:
        threading.Timer(
            1.0,
            lambda: webbrowser.open(f"http://{FLASK_HOST}:{FLASK_PORT}"),
        ).start()

    # EXE mode: Flask in daemon thread, main thread watches for exit.
    if getattr(sys, "frozen", False):
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
        try:
            while not is_shutting_down():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            request_shutdown()
            print("\n  Exiting...", file=sys.stderr)
            flask_thread.join(timeout=3)
            sys.exit(0)
    else:
        try:
            app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)
        except KeyboardInterrupt:
            pass
