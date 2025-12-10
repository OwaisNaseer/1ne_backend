# Quick Start Guide - Fix "Unable to reach server" Error

## The Problem
Frontend cannot connect to backend because:
1. Backend server is not running
2. CORS is not configured (now fixed!)

## Solution Steps

### Step 1: Start the Backend Server

**Option A: Using PowerShell Script (Recommended)**
```powershell
cd 1ne_backend
.\start_server.ps1
```

**Option B: Manual Start**
```powershell
cd 1ne_backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: Using Batch File**
```cmd
cd 1ne_backend
start_server.bat
```

### Step 2: Verify Backend is Running

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 3: Test Backend Connection

**Option A: Use the Python Checker**
```powershell
cd 1ne_backend
.\venv\Scripts\python.exe check_backend.py
```

**Option B: Use Browser Checker**
1. Open `1ne-frontend/check_backend_connection.html` in your browser
2. Click "Run Tests"
3. Verify all tests pass

**Option C: Manual Test**
Open browser and go to:
- Health: http://localhost:8000/health
- Templates: http://localhost:8000/api/v1/templates
- API Docs: http://localhost:8000/docs

### Step 4: Start Frontend

In a **new terminal**:
```powershell
cd 1ne-frontend
npm run dev
```

### Step 5: Test in Browser

1. Open http://localhost:5173
2. Navigate to `/dashboard/templates`
3. Templates should now load!

## What Was Fixed

✅ **Added CORS Middleware** to `app/main.py`
- Allows requests from `http://localhost:5173` (Vite default)
- Allows requests from `http://localhost:3000` (alternative)
- Allows all methods and headers

## Troubleshooting

### Backend Won't Start

**Error: "Module not found"**
```powershell
cd 1ne_backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
- Find and stop the process using port 8000
- Or change port in `start_server.ps1`: `--port 8001`

**Error: "Database connection failed"**
- Ensure PostgreSQL is running
- Check `.env` file has correct database credentials
- Run migrations: `alembic upgrade head`

### Frontend Still Shows Error

1. **Check Backend is Running:**
   - Open http://localhost:8000/health in browser
   - Should return: `{"status": "ok"}`

2. **Check CORS:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Look for CORS errors
   - If you see CORS errors, restart backend (CORS was just added)

3. **Check API URL:**
   - Verify frontend `.env` has: `VITE_API_URL=http://localhost:8000/api`
   - Or check default in `src/api/client.ts`

4. **Clear Browser Cache:**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

## Verification Checklist

- [ ] Backend server is running (see Step 2 output)
- [ ] Health endpoint works: http://localhost:8000/health
- [ ] Templates endpoint works: http://localhost:8000/api/v1/templates
- [ ] Frontend server is running: http://localhost:5173
- [ ] No CORS errors in browser console
- [ ] Templates load in frontend

## Still Having Issues?

1. Check both terminals (backend and frontend) for error messages
2. Check browser console (F12) for detailed errors
3. Check browser Network tab for failed requests
4. Verify ports are not blocked by firewall
5. Try restarting both servers

---

**Note:** CORS middleware has been added to the backend. You need to **restart the backend server** for the changes to take effect!

