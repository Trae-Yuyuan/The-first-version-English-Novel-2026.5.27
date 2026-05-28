from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import uuid
from datetime import datetime

from services.ai_service import process_translation

app = Flask(__name__)

# 🚨 允许 Electron 调用（必须）
CORS(app, resources={r"/*": {"origins": "*"}})

# =========================
# STREAM API
# =========================
@app.route("/process", methods=["POST"])
def process():

    novel = request.files.get("novel")
    vocab = request.files.get("vocab")
    api_key = request.form.get("api_key")

    if not novel or not vocab or not api_key:
        return jsonify({"error": "missing input"}), 400

    novel_path = "temp_novel.txt"
    vocab_path = "temp_vocab.txt"

    novel.save(novel_path)
    vocab.save(vocab_path)

    result = process_translation(novel_path, vocab_path, api_key)
    full_text = result["text"]

    task_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate():
        for char in full_text:
            yield f"data: {json.dumps({'char': char})}\n\n"

        yield f"data: {json.dumps({
            'done': True,
            'task_id': task_id,
            'created_at': created_at
        })}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )


# =========================
# HEALTH CHECK（新增）
# =========================
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )