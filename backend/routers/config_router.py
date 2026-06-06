"""Configuration routes.

GET  /api/config       — return current persistent config (all keys)
POST /api/config       — update config keys
GET  /api/config/status — return non-sensitive app info (port, modes, health)
"""

from flask import request, jsonify
from config_manager import config_manager


def register_config_routes(app):
    """Register config routes on the Flask app."""

    @app.route("/api/config", methods=["GET"])
    def api_get_config():
        """Return all persistent configuration."""
        return jsonify(config_manager.get_config())

    @app.route("/api/config", methods=["POST"])
    def api_update_config():
        """Update persistent configuration keys.

        Body: JSON object with one or more of the known keys.
        """
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        safe = {}
        for key in config_manager.DEFAULTS:
            if key in data and isinstance(data[key], str):
                safe[key] = data[key].strip()

        if safe:
            config_manager.update_config(safe)

        return jsonify({"status": "ok", "updated": list(safe.keys())})

    @app.route("/api/config/status", methods=["GET"])
    def api_config_status():
        """Return non-sensitive application status."""
        cfg = config_manager.get_config()
        return jsonify({
            "modes": ["debate", "discuss", "translate"],
            "has_api_key": bool(cfg.get("api_key")),
            "has_debate_bot": bool(cfg.get("bot_id_debate")),
            "has_discuss_bot": bool(cfg.get("bot_id_discuss")),
        })
