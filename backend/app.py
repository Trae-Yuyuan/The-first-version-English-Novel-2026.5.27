"""Flask API server for AI novel translation."""

import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from translator import translate
from config import FLASK_PORT, MAX_CONTENT_LENGTH

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


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


if __name__ == "__main__":
    app.run(debug=True, port=FLASK_PORT)
