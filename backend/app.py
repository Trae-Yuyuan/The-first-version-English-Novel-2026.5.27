from flask import (
    Flask,
    request,
    jsonify,
    Response,
    stream_with_context,
    send_from_directory
)

from flask_cors import CORS

import json
import uuid
import os

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

    # =========================
    # INPUT CHECK
    # =========================
    if not novel or not vocab or not api_key:

        return jsonify({
            "error": "missing input"
        }), 400

    # =========================
    # TEMP FILES
    # =========================
    novel_path = "temp_novel.txt"
    vocab_path = "temp_vocab.txt"

    novel.save(novel_path)
    vocab.save(vocab_path)

    # =========================
    # AI PROCESS
    # =========================
    result = process_translation(
        novel_path,
        vocab_path,
        api_key
    )

    full_text = result["text"]

    # =========================
    # SAVE OUTPUT FILE
    # =========================
    os.makedirs("outputs", exist_ok=True)

    output_filename = "output.txt"

    output_path = os.path.join(
        "outputs",
        output_filename
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(full_text)

    # =========================
    # TASK META
    # =========================
    task_id = str(uuid.uuid4())[:8]

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # =========================
    # STREAM RESPONSE
    # =========================
    def generate():

        # STREAM CHAR BY CHAR
        for char in full_text:

            chunk = {
                "char": char
            }

            yield (
                f"data: "
                f"{json.dumps(chunk)}"
                f"\n\n"
            )

        # DONE EVENT
        done_data = {
            "done": True,
            "task_id": task_id,
            "created_at": created_at,
            "download_url": f"/download/{output_filename}"
        }

        yield (
            f"data: "
            f"{json.dumps(done_data)}"
            f"\n\n"
        )

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream"
    )

# =========================
# DOWNLOAD SYSTEM
# =========================
@app.route("/download/<filename>")
def download(filename):

    return send_from_directory(
        "outputs",
        filename,
        as_attachment=True
    )

# =========================
# START
# =========================
if __name__ == "__main__":

    os.makedirs("outputs", exist_ok=True)

    app.run(
        debug=True,
        port=5000
    )