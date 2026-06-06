"""Translation route — DeepSeek-powered novel-to-English translator.

POST /api/translate
  Body: { api_key: str, novel_text: str, vocab_text: str }
  Returns: { translated_text: str, highlights: [{word, start, end}] }
"""

import traceback
from flask import request, jsonify
from translator import translate


def register_translate_routes(app):
    """Register the translation route on the Flask app."""

    @app.route("/api/translate", methods=["POST"])
    def handle_translate():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        api_key = (data.get("api_key", "") or "").strip()
        novel_text = (data.get("novel_text", "") or "").strip()
        vocab_text = (data.get("vocab_text", "") or "").strip()

        if not api_key:
            return jsonify({"error": "API Key is required"}), 400
        if not novel_text:
            return jsonify({"error": "Novel text is required"}), 400

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
                return jsonify(
                    {"error": "Invalid API Key. Please check your DeepSeek API key."}
                ), 401
            if "402" in error_msg or "insufficient" in error_msg.lower():
                return jsonify(
                    {"error": "Insufficient balance. Please top up your DeepSeek account."}
                ), 402
            return jsonify({"error": f"Translation failed: {error_msg}"}), 500
