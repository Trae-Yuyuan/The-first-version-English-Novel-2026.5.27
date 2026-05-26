from flask import Blueprint, request, jsonify
from services.ai_service import process_files

process_bp = Blueprint("process", __name__)

@process_bp.route("/api/process", methods=["POST"])
def process():
    try:
        novel = request.files.get("novel")
        vocab = request.files.get("vocab")

        if not novel or not vocab:
            return jsonify({"error": "missing files"}), 400

        result = process_files(novel, vocab)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500