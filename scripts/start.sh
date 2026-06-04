#!/usr/bin/env bash
# ============================================================
# AI Novel Translator — Linux/macOS One-Click Start Script
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "  AI Novel Translator — Starting..."
echo "========================================"

# --- Backend ---
echo ""
echo "[1/2] Starting Python backend..."

BACKEND_DIR="$PROJECT_ROOT/backend"
VENV_DIR="$BACKEND_DIR/venv"

# Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate and install dependencies
source "$VENV_DIR/bin/activate"
echo "  Installing Python dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt" -q

# Start Flask in background
python "$BACKEND_DIR/app.py" &
FLASK_PID=$!
echo "  Flask backend running on http://localhost:5000 (PID: $FLASK_PID)"

# --- Frontend ---
echo ""
echo "[2/2] Starting React frontend..."

FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Install npm dependencies if missing
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "  Installing npm packages..."
    cd "$FRONTEND_DIR"
    npm install
    cd "$PROJECT_ROOT"
fi

# Trap to kill Flask on exit
trap 'echo ""; echo "Shutting down Flask (PID: $FLASK_PID)..."; kill $FLASK_PID 2>/dev/null; exit 0' SIGINT SIGTERM

echo "  Vite frontend running on http://localhost:5173"
echo ""
echo "========================================"
echo "  Open http://localhost:5173 in browser"
echo "  Press Ctrl+C to stop"
echo "========================================"

cd "$FRONTEND_DIR"
npm run dev
