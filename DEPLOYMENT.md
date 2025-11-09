# Deployment Guide

## Step 1: Initialize Git Repository

```bash
cd C:\Users\Vijay Mane\Desktop\task_SHL

# Initialize git
git init

# Add files
git add .
git commit -m "Initial commit: SHL Assessment Recommendation System"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `shl-assessment-recommender`
3. Description: "Intelligent recommendation system for SHL assessments using semantic search"
4. **Keep it Public** (or private and share access with SHL)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

## Step 3: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/shl-assessment-recommender.git

# Push code
git branch -M main
git push -u origin main
```

## Step 4: Deploy Backend API to Render

### Option A: Automatic Deployment (Recommended)

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `shl-assessment-api`
   - **Environment**: Python 3
   - **Build Command**: `bash build.sh`
   - **Start Command**: `bash start.sh`
   - **Instance Type**: Free
5. Click "Create Web Service"
6. Wait for deployment (5-10 minutes first time)
7. Copy your API URL (e.g., `https://shl-assessment-api.onrender.com`)

### Option B: Alternative Platforms

**Railway.app**:
1. Go to https://railway.app
2. "New Project" → Import from GitHub
3. Add service: backend
4. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
5. Deploy

**Fly.io**:
```bash
flyctl launch
flyctl deploy
```

## Step 5: Deploy Frontend

### Option A: Vercel (Recommended for Frontend)

1. Go to https://vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
5. **Update API URL** in `frontend/app.js`:
   ```javascript
   const API_URL = "https://your-backend-url.onrender.com";
   ```
6. Deploy

### Option B: GitHub Pages

1. Update `frontend/app.js` with deployed API URL
2. Commit changes:
   ```bash
   git add frontend/app.js
   git commit -m "Update API URL for production"
   git push
   ```
3. Go to GitHub repo → Settings → Pages
4. Source: Deploy from a branch → `main` → `/frontend`
5. Save
6. Frontend will be available at: `https://YOUR_USERNAME.github.io/shl-assessment-recommender/`

### Option C: Netlify

1. Go to https://netlify.com
2. "New site from Git"
3. Choose repository
4. **Publish directory**: `frontend`
5. Deploy

## Step 6: Test Deployed System

1. **Test Health Endpoint**:
   ```bash
   curl https://your-backend-url.onrender.com/health
   ```

2. **Test Recommend Endpoint**:
   ```bash
   curl -X POST https://your-backend-url.onrender.com/recommend \
     -H "Content-Type: application/json" \
     -d '{"query": "I need Java developers"}'
   ```

3. **Test Frontend**:
   - Open your frontend URL in browser
   - Enter a test query
   - Verify results display correctly

## Submission Checklist

✅ **3 URLs Required**:

1. **API Endpoint**: `https://your-backend.onrender.com`
2. **GitHub Repository**: `https://github.com/YOUR_USERNAME/shl-assessment-recommender`
3. **Frontend URL**: `https://your-frontend.vercel.app`

✅ **Files to Submit**:

1. **predictions.csv** (already generated)
2. **APPROACH.md** (2-page technical document)
3. URLs via submission form

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify `requirements.txt` is complete
- Ensure `data/assessments.csv` exists or scraper runs during build

### Frontend can't reach API
- Check CORS is enabled in `backend/app.py` (already set to `allow_origins=["*"]`)
- Verify API URL in `frontend/app.js` is correct
- Check API is responding to `/health`

### Embeddings not loading
- First deployment takes longer (~10 min) to download sentence-transformers model
- Check Render build logs for progress
- Model is cached after first download

## Free Tier Limits

**Render**:
- 750 hours/month (enough for 1 service 24/7)
- Sleeps after 15 min inactivity (first request takes ~30 sec to wake)
- 512 MB RAM

**Vercel**:
- Unlimited static deployments
- 100 GB bandwidth/month

**Railway**:
- $5 free credit/month
- ~500 hours of runtime

