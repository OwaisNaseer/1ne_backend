# Start server script with proper error handling
Write-Host "Starting 1ne.ai Backend Server..." -ForegroundColor Green

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$checkDep = .\venv\Scripts\python.exe -c "import fastapi, uvicorn; print('OK')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Dependencies not installed!" -ForegroundColor Red
    Write-Host "Please run: .\venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Dependencies OK" -ForegroundColor Green

# Start server
Write-Host "`nStarting server on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

