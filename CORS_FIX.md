# CORS Fix for Vercel Frontend Deployment

## Issue
Frontend deployed on Vercel cannot connect to Railway backend due to CORS restrictions.

## Solution
The backend CORS configuration has been updated to use the `FRONTEND_URL` environment variable.

## Steps to Fix

### 1. Get Your Vercel Frontend URL
- Go to your Vercel dashboard
- Find your deployed frontend project
- Copy the production URL (e.g., `https://your-app.vercel.app`)

### 2. Update Railway Environment Variables
1. Go to Railway dashboard → Your backend service
2. Click on **Variables** tab
3. Add or update the following variable:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ```
   Replace `your-app.vercel.app` with your actual Vercel URL

### 3. Redeploy Backend (if needed)
- Railway will automatically redeploy when environment variables change
- Or manually trigger a redeploy from Railway dashboard

### 4. Verify CORS is Working
Test the connection from your Vercel frontend:
- Open browser console
- Try to make an API request
- Check for CORS errors

## Alternative: Allow All Origins (Not Recommended for Production)
If you need to allow all origins temporarily (for testing), you can set:
```
ENVIRONMENT=dev
```
This will allow all origins (`["*"]`), but is **NOT recommended for production**.

## Current CORS Configuration
The backend now:
- Uses `FRONTEND_URL` environment variable for the primary frontend URL
- Still allows localhost origins for local development
- Supports Vercel preview deployments via `VERCEL_URL` environment variable

## Testing
After updating `FRONTEND_URL`:
1. Wait for Railway to redeploy (if needed)
2. Test from your Vercel frontend
3. Check browser console for any CORS errors
4. Verify API requests are working
