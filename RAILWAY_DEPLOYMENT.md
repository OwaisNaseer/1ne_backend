# Railway Deployment Guide for Demo Branch

This guide explains how to deploy the `demo` branch of the 1ne.ai backend to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Your repository connected to Railway
3. PostgreSQL database provisioned on Railway

## Step 1: Connect Your Repository to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"** (or GitLab/Bitbucket)
4. Select your repository containing the `1ne_backend` folder
5. Railway will automatically detect it as a Python project

## Step 2: Configure Branch Deployment

1. In your Railway project, go to **Settings**
2. Under **"Source"**, you'll see the branch configuration
3. Change the branch from `main` to `demo`:
   - Click on the branch dropdown
   - Select `demo` branch
   - Railway will automatically redeploy from the `demo` branch

Alternatively, you can:
- Go to **Settings** → **Source**
- Set **"Production Branch"** to `demo`
- Or create a separate service for the demo branch

## Step 3: Configure Environment Variables

In Railway, go to your service → **Variables** tab and add the following:

### Required Variables

```env
# Database (Railway will provide this if you use Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Environment
ENVIRONMENT=production

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256

# Frontend URL (update with your frontend URL)
FRONTEND_URL=https://your-frontend-domain.com

# Email Configuration (if using email features)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@1ne.ai
SMTP_FROM_NAME=1ne.ai
```

### Optional LLM Provider Keys

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google
GOOGLE_API_KEY=your-google-api-key
```

### Generate a Secure Secret Key

For production, generate a secure secret key:

```bash
# Using OpenSSL
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Set Up PostgreSQL Database

1. In Railway, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL database
3. The `DATABASE_URL` will be automatically set as an environment variable
4. You can reference it in your service as `${{Postgres.DATABASE_URL}}`

## Step 5: Run Database Migrations

After deployment, you need to run Alembic migrations:

### Option 1: Using Railway CLI

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Run migrations:
   ```bash
   railway run alembic upgrade head
   ```

### Option 2: Using Railway Shell

1. In Railway dashboard, go to your service
2. Click on **"Deployments"** → **"View Logs"**
3. Click **"Shell"** tab
4. Run:
   ```bash
   alembic upgrade head
   ```

### Option 3: One-time Migration Service

Create a temporary service that runs migrations on startup (then disable it after first run).

## Step 6: Deploy

1. Railway will automatically deploy when you:
   - Push to the `demo` branch
   - Change environment variables
   - Manually trigger a redeploy

2. Monitor the deployment:
   - Go to **"Deployments"** tab
   - Watch the build logs
   - Check for any errors

3. Once deployed, Railway will provide a URL like:
   ```
   https://your-service-name.up.railway.app
   ```

## Step 7: Verify Deployment

1. **Health Check:**
   ```bash
   curl https://your-service-name.up.railway.app/health
   ```
   Should return: `{"status": "ok"}`

2. **API Documentation:**
   Visit: `https://your-service-name.up.railway.app/docs`

3. **Test Endpoints:**
   Use the interactive Swagger UI at `/docs` to test your endpoints

## Step 8: Configure Custom Domain (Optional)

1. In Railway, go to your service → **Settings**
2. Under **"Domains"**, click **"Generate Domain"** or **"Custom Domain"**
3. Follow the DNS configuration instructions

## Troubleshooting

### Build Fails

- Check build logs in Railway dashboard
- Ensure `requirements.txt` is up to date
- Verify Python version compatibility (3.11+)

### Database Connection Issues

- Verify `DATABASE_URL` is correctly set
- Check that PostgreSQL service is running
- Ensure database migrations have been run

### Application Crashes

- Check application logs in Railway
- Verify all required environment variables are set
- Check for port binding issues (Railway sets `$PORT` automatically)

### CORS Issues

- Update `FRONTEND_URL` environment variable
- Check CORS configuration in `app/main.py`

## Important Notes

1. **Never commit `.env` files** - Use Railway's environment variables instead
2. **Use Railway's PostgreSQL** - It automatically handles connection pooling and backups
3. **Monitor logs** - Railway provides real-time logs for debugging
4. **Set up health checks** - Railway can monitor your `/health` endpoint
5. **Use Railway's secrets** - For sensitive data like API keys

## Updating Deployment

To update your deployment:

1. Push changes to the `demo` branch
2. Railway will automatically detect and deploy
3. Or manually trigger redeploy from Railway dashboard

## Branch-Specific Deployment

If you want to deploy multiple branches:

1. Create separate services for each branch
2. Or use Railway's branch-based deployments feature
3. Configure each service to watch a specific branch

---

For more information, visit [Railway Documentation](https://docs.railway.app)
