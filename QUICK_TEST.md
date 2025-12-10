# Quick Endpoint Testing Guide

## Issue Fixed: Hanging Commands
All test scripts have been updated to prevent hanging. Use the instructions below.

## Step-by-Step Testing

### 1. Install Dependencies (One Time)
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start Server (Terminal 1)
```powershell
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```
**Wait for:** `Uvicorn running on http://127.0.0.1:8000`

### 3. Run Tests (Terminal 2)
```powershell
.\venv\Scripts\activate
python test_api_endpoints.py
```

## Manual Quick Tests

### Test 1: Health Check
```powershell
curl http://localhost:8000/health
```
**Expected:** `{"status":"ok"}`

### Test 2: List Templates
```powershell
curl http://localhost:8000/api/v1/templates
```

### Test 3: Non-Streaming Execute
```powershell
curl -X POST http://localhost:8000/api/v1/templates/lesson_planner/execute ^
  -H "Content-Type: application/json" ^
  -d "{\"data\":{\"subject\":\"science\",\"grade\":5,\"topic\":\"Test\",\"learning_objective\":\"Test\",\"time_duration\":\"45 min\",\"bloom_level\":\"Understand\",\"differentiation_needs\":false}}"
```

### Test 4: Streaming Execute
```powershell
curl -X POST http://localhost:8000/api/v1/templates/lesson_planner/execute-stream ^
  -H "Content-Type: application/json" ^
  -d "{\"data\":{\"subject\":\"science\",\"grade\":5,\"topic\":\"Test\",\"learning_objective\":\"Test\",\"time_duration\":\"45 min\",\"bloom_level\":\"Understand\",\"differentiation_needs\":false}}"
```

## Test Results Summary

After running `test_api_endpoints.py`, you should see:

```
[PASS] - Server Health Check
[PASS] - List Templates
[PASS] - Get Template Detail  
[PASS] - Non-Streaming Execution
[PASS] - Streaming Execution

[SUCCESS] All tests passed!
```

## Troubleshooting

**If tests fail:**
1. Check server is running: `curl http://localhost:8000/health`
2. Check database: Run `alembic upgrade head`
3. Seed templates: `python -m app.seed.cli`
4. Check .env file exists with DATABASE_URL

**If server won't start:**
- Check port 8000 is free
- Verify dependencies: `pip list | findstr fastapi`
- Check for import errors in terminal output

