"""Graceful shutdown for Flask EXE.

Ensures the process exits cleanly when the user closes the browser window
or the console — no lingering background processes that prevent file deletion.

On Windows (PyInstaller EXE), closing the console sends CTRL_CLOSE_EVENT.
On all platforms, SIGINT / SIGTERM trigger a clean exit.
"""

import atexit
import os
import signal
import sys
import threading

# Global event — when set, all threads should wind down.
_shutdown_event = threading.Event()

# Optional reference to a health-check thread so we can join it.
_health_thread = None


def is_shutting_down() -> bool:
    """Check whether shutdown has been requested."""
    return _shutdown_event.is_set()


def request_shutdown() -> None:
    """Signal that the application should exit."""
    _shutdown_event.set()


def _on_exit():
    """atexit handler — ensures the event is set so any polling loop exits."""
    _shutdown_event.set()
    # Give daemon threads a moment to finish.
    if _health_thread and _health_thread.is_alive():
        _health_thread.join(timeout=2)


def _signal_handler(signum, frame):
    """Handle SIGINT / SIGTERM."""
    print(f"\n  Shutting down (signal {signum})...", file=sys.stderr)
    request_shutdown()
    # Force exit after a short grace period in case threads are stuck.
    threading.Timer(3.0, lambda: os._exit(0)).start()


def _setup_windows_console_handler():
    """Register a Windows console control handler (CTRL_CLOSE_EVENT etc.)."""
    if sys.platform != "win32":
        return
    try:
        import win32api
        import win32con

        def _win_handler(event):
            if event in (
                win32con.CTRL_CLOSE_EVENT,
                win32con.CTRL_C_EVENT,
                win32con.CTRL_BREAK_EVENT,
                win32con.CTRL_SHUTDOWN_EVENT,
            ):
                print(f"\n  Console event {event} — shutting down...", file=sys.stderr)
                request_shutdown()
                # Let the main thread exit naturally; don't return True (which
                # would suppress further handling).
            return False

        win32api.SetConsoleCtrlHandler(_win_handler, True)
    except ImportError:
        # pywin32 not installed — fall back to signal-only handling.
        pass


def register_shutdown_handlers():
    """Call once at startup to register all exit handlers.

    Should be called in the ``if __name__ == "__main__":`` block of app.py
    BEFORE starting the Flask server.
    """
    atexit.register(_on_exit)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    _setup_windows_console_handler()

    # In EXE mode, also spawn a health-watchdog thread: if the Flask server
    # is unreachable for a while (user closed browser, etc.), auto-shutdown.
    if getattr(sys, "frozen", False):
        _start_watchdog()


def _start_watchdog():
    """Background thread: if no HTTP requests come for a long idle window,
    assume the user has walked away / closed the browser and exit.

    The idle timeout is generous (5 minutes) — any API call resets it.
    """
    import time
    import urllib.request

    IDLE_TIMEOUT = 300  # seconds
    CHECK_INTERVAL = 10

    def _watchdog():
        last_alive = time.time()
        health_url = "http://127.0.0.1:5000/api/health"

        while not _shutdown_event.is_set():
            time.sleep(CHECK_INTERVAL)
            try:
                urllib.request.urlopen(health_url, timeout=3)
                # Server is reachable — reset idle timer.
                last_alive = time.time()
            except Exception:
                # Server unreachable — check if timeout exceeded.
                if time.time() - last_alive > IDLE_TIMEOUT:
                    print(
                        "  Watchdog: idle timeout — shutting down.",
                        file=sys.stderr,
                    )
                    request_shutdown()
                    return

    global _health_thread
    _health_thread = threading.Thread(target=_watchdog, daemon=True)
    _health_thread.start()
