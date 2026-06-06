"""Unified persistent configuration manager.

Stores user settings (API keys, Bot IDs, etc.) in a single config.json
file located alongside the EXE (or alongside this script in dev mode).

Thread-safe — uses a lock to prevent concurrent write corruption.
"""

import json
import os
import sys
import threading


class ConfigManager:
    """Singleton-style config with atomic file I/O.

    Usage:
        from config_manager import config_manager
        cfg = config_manager.get_config()
        config_manager.update_config({"api_key": "pat_xxx"})
    """

    DEFAULTS = {
        "api_key": "",
        "bot_id_debate": "",
        "bot_id_discuss": "",
        "coze_api_url": "",
        "deepseek_api_key": "",
        "last_session_id": "",
    }

    def __init__(self):
        # EXE mode: config lives next to the .exe
        # Dev mode: config lives in the backend/ directory
        if getattr(sys, "frozen", False):
            config_dir = os.path.dirname(sys.executable)
        else:
            config_dir = os.path.dirname(os.path.abspath(__file__))

        self._config_path = os.path.join(config_dir, "config.json")
        self._lock = threading.Lock()
        self._ensure_file()

    # ── internal helpers ────────────────────────────────────────────

    def _ensure_file(self):
        """Create config.json with defaults if it doesn't exist."""
        if not os.path.exists(self._config_path):
            self._write(self.DEFAULTS.copy())

    def _read(self) -> dict:
        """Read + parse config.json. Returns a fresh dict every call."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if not isinstance(data, dict):
                    return self.DEFAULTS.copy()
                # Merge with defaults so new keys are always present
                merged = self.DEFAULTS.copy()
                merged.update(data)
                return merged
        except (json.JSONDecodeError, IOError, OSError):
            return self.DEFAULTS.copy()

    def _write(self, data: dict) -> None:
        """Atomically write config to disk (write-to-temp + rename)."""
        tmp = self._config_path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            os.replace(tmp, self._config_path)  # atomic on Windows
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    # ── public API ──────────────────────────────────────────────────

    def get_config(self) -> dict:
        """Return the full configuration dictionary (thread-safe)."""
        with self._lock:
            return self._read()

    def set_config(self, key: str, value) -> None:
        """Set a single config key and persist immediately."""
        with self._lock:
            data = self._read()
            data[key] = value
            self._write(data)

    def update_config(self, updates: dict) -> None:
        """Merge a dict of updates into config and persist.

        Example:
            config_manager.update_config({
                "api_key": "pat_new",
                "bot_id_debate": "bot_123",
            })
        """
        with self._lock:
            data = self._read()
            data.update(updates)
            self._write(data)

    def clear_config(self) -> None:
        """Reset config to factory defaults."""
        with self._lock:
            self._write(self.DEFAULTS.copy())

    @property
    def path(self) -> str:
        return self._config_path


# Module-level singleton — import this, don't instantiate ConfigManager directly.
config_manager = ConfigManager()
