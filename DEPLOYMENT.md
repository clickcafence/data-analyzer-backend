# Deployment Instructions

## Prerequisites
- GitHub account
- Render.com account (free tier available)
- Git installed locally

## Step 1: Prepare Your Local Repository

1. Remove venv and __pycache__ from git tracking:
```bash
git rm -r --cached venv/
git rm -r --cached __pycache__/
git rm -r --cached .vscode/
```

2. Commit the new deployment files:
```bash
git add requirements.txt .gitignore render.yaml Procfile runtime.txt
git add frontend/.env.example
git commit -m "Add deployment configuration files"
git push origin main
```

## Step 2: Build Frontend for Production

1. Navigate to frontend directory:
```bash
cd frontend
npm install
npm run build
```

2. Copy the dist folder to backend:
```bash
cp -r dist ../public
cd ..
```

3. Update main.py to serve the frontend (add after CORS middleware):

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Serve static frontend files
frontend_path = Path(__file__).parent / "public"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
```

## Step 3: Deploy on Render

1. Go to https://render.com and sign up/login
2. Click "New +" → "Web Service"
3. Select "Deploy from GitHub"
4. Choose your repository
5. Configure:
   - **Name**: data-analyzer-backend (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && cp -r frontend/dist public`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Region**: Choose closest to you (US is default)
6. Click "Create Web Service"

Render will automatically deploy and give you a URL like `https://data-analyzer-backend.onrender.com`

## Step 4: Update Frontend Environment

1. Create `frontend/.env.production` with:
```
VITE_API_URL=https://your-deployed-url.onrender.com
```

2. Or set environment variable in Render dashboard:
   - Go to your service
   - Settings → Environment Variables
   - Add: `VITE_API_URL=https://your-deployed-url.onrender.com`

## Step 5: Redeploy

Push a new commit to trigger redeployment:
```bash
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

## Troubleshooting

- **502 Bad Gateway**: Check build logs in Render (Logs tab)
- **CORS errors**: Verify CORS middleware in main.py allows your frontend domain
- **Frontend not loading**: Make sure frontend build succeeded and public/ folder exists
- **API calls failing**: Check that VITE_API_URL environment variable is set

## Local Development

For local development, you can use separate terminals:

Terminal 1 (Backend):
```bash
.venv\Scripts\activate
uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then visit http://localhost:5173 in your browser.

## Cost

- **Render Free Tier**: 750 hours/month (roughly 31 days continuous), perfect for testing
- **Paid**: $7/month for always-on service
- **Database**: Not needed for your app (stateless)

Good luck with your deployment! 🚀
