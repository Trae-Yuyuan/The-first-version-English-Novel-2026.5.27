"""Flask API server for AI novel translation.

Supports both:
- Dev mode: Vite dev server proxies /api to Flask (port 5000)
- Production/EXE mode: Flask serves built frontend + API on same port
"""

import os
import sys
import traceback
import mimetypes
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from translator import translate
from config import FLASK_PORT, FLASK_HOST, MAX_CONTENT_LENGTH

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

@app.route("/api/translate", methods=["POST"])
def handle_translate():
    """
    POST /api/translate
    Body: { api_key: str, novel_text: str, vocab_text: str }
    Returns: { translated_text: str, highlights: [{word, start, end}] }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    api_key = data.get("api_key", "").strip()
    novel_text = data.get("novel_text", "").strip()
    vocab_text = data.get("vocab_text", "").strip()

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


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


# ── Frontend Static Serving (production / EXE mode) ────────────────────────

@app.route("/")
def serve_index():
    """Serve the frontend entry point."""
    if HAS_STATIC:
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"error": "Frontend not built. Run: cd frontend && npm run build"}), 404


@app.route("/<path:path>")
def serve_frontend(path):
    """
    Serve frontend assets with SPA fallback.
    - API routes are matched first (registered above).
    - If the path matches a real file in STATIC_DIR, serve it.
    - Otherwise return index.html (SPA client-side routing).
    """
    if HAS_STATIC:
        file_path = os.path.join(STATIC_DIR, path)
        if os.path.isfile(file_path):
            mimetype, _ = mimetypes.guess_type(file_path)
            return send_from_directory(
                STATIC_DIR, path, mimetype=mimetype
            )
        # SPA fallback — let React handle the route
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"error": "Not found"}), 404


# ── Startup ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import webbrowser
    import threading

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
    # In dev mode, Vite opens its own browser tab on port 5173.
    if HAS_STATIC:
        threading.Timer(1.0, open_browser).start()

    app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT)
