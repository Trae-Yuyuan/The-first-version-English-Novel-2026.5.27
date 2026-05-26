from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import uuid
from datetime import datetime

from services.ai_service import process_translation

app = Flask(__name__)
CORS(app)

# =========================
# STREAM + TASK SYSTEM
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

    # =========================
    # TASK META
    # =========================
    task_id = str(uuid.uuid4())[:8]
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =========================
    # STREAM RESPONSE
    # =========================
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
# DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    from flask import send_from_directory
    return send_from_directory("outputs", filename, as_attachment=True)


# =========================
# START
# =========================
if __name__ == "__main__":
    app.run(debug=True, port=5000)