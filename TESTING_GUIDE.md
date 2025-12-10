# Testing Guide - 1ne.ai Backend

## Quick Start Testing

### Step 1: Check Status
```powershell
# Check if everything is set up
.\venv\Scripts\python.exe -c "import fastapi, uvicorn; print('Dependencies OK')"
```

### Step 2: Start Server
```powershell
# In one terminal window
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Run Tests
```powershell
# In another terminal window
.\venv\Scripts\activate
python test_api_endpoints.py
```

## Manual Testing

### 1. Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```
**Expected:** `{"status": "ok"}`

### 2. List Templates
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/templates" -Method Get
```
**Expected:** Array of template objects

### 3. Get Template Detail
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/templates/lesson_planner" -Method Get
```
**Expected:** Template detail with latest version

### 4. Non-Streaming Execution
```powershell
$payload = @{
    data = @{
        subject = "science"
        grade = 5
        topic = "Earth's Rotation"
        learning_objective = "Students will understand rotation"
        time_duration = "45 min"
        bloom_level = "Understand"
        differentiation_needs = $false
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/templates/lesson_planner/execute" -Method Post -Body $payload -ContentType "application/json"
```
**Expected:** Execution response with output data

### 5. Streaming Execution
```powershell
$payload = @{
    data = @{
        subject = "science"
        grade = 5
        topic = "Earth's Rotation"
        learning_objective = "Students will understand rotation"
        time_duration = "45 min"
        bloom_level = "Understand"
        differentiation_needs = $false
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/templates/lesson_planner/execute-stream" -Method Post -Body $payload -ContentType "application/json" -TimeoutSec 120

# Parse SSE events
$response.Content -split "`n`n" | Where-Object { $_ -match "data:" } | ForEach-Object {
    $json = ($_ -replace "data: ", "") | ConvertFrom-Json
    Write-Output "Type: $($json.type)"
}
```
**Expected:** SSE stream with content chunks and done event

## Test Script

The `test_api_endpoints.py` script automatically tests all endpoints:

```powershell
python test_api_endpoints.py
```

This will test:
- ✓ Health check
- ✓ List templates
- ✓ Get template detail
- ✓ Non-streaming execution
- ✓ Streaming execution

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check `.env` file exists with correct DATABASE_URL

### Tests fail with 404
- Run database migrations: `alembic upgrade head`
- Seed templates: `python -m app.seed.cli`

### Streaming doesn't work
- Check `USE_REAL_LLM=true` in `.env`
- Verify `OPENAI_API_KEY` is set correctly
- Check server logs for errors

## Expected Results

### Non-Streaming Endpoint
- Returns complete response immediately
- Includes `execution_id`, `model_used`, `provider_used`
- Contains full `output` object

### Streaming Endpoint
- Returns `text/event-stream` content type
- Emits `meta` event first
- Emits multiple `content` events with chunks
- Emits `done` event with `execution_id` at the end

