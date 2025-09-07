# VEDYA Deployment Guide

## Architecture Overview
- **Frontend**: Next.js deployed on Vercel
- **Backend**: Python FastAPI deployed on Railway/Render
- **Database**: Supabase PostgreSQL (already configured)
- **Authentication**: Clerk (works with both platforms)

## Option 1: Railway (Recommended for Python)

### Backend Deployment (Railway)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway new

# 4. Add environment variables to Railway
railway variables set OPENAI_API_KEY=your_key
railway variables set DATABASE_URL=your_supabase_url
# ... add all other env vars

# 5. Deploy
railway up
```

### Frontend Deployment (Vercel)
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy frontend
cd frontend
vercel --prod

# 3. Set environment variables in Vercel dashboard
# - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# - CLERK_SECRET_KEY
# - NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
```

## Option 2: Render

### Backend on Render
1. Connect GitHub repo to Render
2. Create Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### Frontend on Vercel
Same as above, but point to Render backend URL

## Option 3: All-in-One Solutions

### Option 3A: DigitalOcean App Platform
- Can host both Python and Node.js
- More expensive but simpler
- Single platform for everything

### Option 3B: AWS (if you want enterprise-grade)
- Frontend: AWS Amplify
- Backend: AWS Lambda + API Gateway (for serverless) or ECS (for containers)
- Database: Already have Supabase, or use AWS RDS

## Environment Variable Management

### Frontend (.env.local)
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (Railway/Render)
```env
# Copy all variables from current .env except frontend-specific ones
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgres://...
SUPABASE_URL=https://...
# ... all other backend vars
```

## Recommended Setup: Railway + Vercel

**Pros:**
- Railway excellent for Python apps
- Vercel excellent for Next.js
- Both have great free tiers
- Easy CI/CD with GitHub
- Good performance globally

**Cons:**
- Two platforms to manage
- Need to configure CORS between domains
