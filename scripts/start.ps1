# ============================================================
# AI Novel Translator — Windows One-Click Start Script
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $projectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Novel Translator — Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# --- Start Backend ---
Write-Host "`n[1/2] Starting Python backend..." -ForegroundColor Yellow

$backendDir = Join-Path $projectRoot "backend"

# Create virtual environment if missing
$venvDir = Join-Path $backendDir "venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "  Creating Python virtual environment..." -ForegroundColor Gray
    python -m venv $venvDir
}

# Activate and install dependencies
$activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
& $activateScript
Write-Host "  Installing Python dependencies..." -ForegroundColor Gray
pip install -r (Join-Path $backendDir "requirements.txt") -q

# Start Flask in background
$flaskJob = Start-Job -Name "FlaskBackend" -ArgumentList $backendDir, $venvDir -ScriptBlock {
    param($dir, $venv)
    & (Join-Path $venv "Scripts\python.exe") (Join-Path $dir "app.py")
}
Write-Host "  Flask backend running on http://localhost:5000" -ForegroundColor Green

# --- Start Frontend ---
Write-Host "`n[2/2] Starting React frontend..." -ForegroundColor Yellow

$frontendDir = Join-Path $projectRoot "frontend"

# Install npm dependencies if node_modules is missing
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "  Installing npm packages..." -ForegroundColor Gray
    Push-Location $frontendDir
    npm install
    Pop-Location
}

# Start Vite dev server in foreground
Write-Host "  Vite frontend running on http://localhost:5173" -ForegroundColor Green
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Open http://localhost:5173 in browser" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Push-Location $frontendDir
npm run dev
Pop-Location

# Cleanup
Write-Host "`nShutting down..." -ForegroundColor Yellow
Stop-Job -Name "FlaskBackend" -ErrorAction SilentlyContinue
Remove-Job -Name "FlaskBackend" -ErrorAction SilentlyContinue
