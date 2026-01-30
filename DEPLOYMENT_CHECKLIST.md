# ✅ Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## Pre-Deployment (Local Setup)

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Git configured with GitHub credentials
- [ ] Repository cloned locally
- [ ] Virtual environment created and activated
- [ ] `pip install -r requirements.txt` successful
- [ ] Backend starts without errors: `uvicorn main:app --reload`
- [ ] Frontend dependencies installed: `cd frontend && npm install`
- [ ] Frontend runs locally: `npm run dev`
- [ ] App works correctly at `http://localhost:5173`

## Code Preparation

- [ ] All deployment files created:
  - [ ] `requirements.txt` ✓
  - [ ] `.gitignore` ✓
  - [ ] `Procfile` ✓
  - [ ] `render.yaml` ✓
  - [ ] `runtime.txt` ✓
  - [ ] `DEPLOYMENT.md` ✓
  - [ ] `README.md` ✓
  - [ ] `QUICKSTART.md` ✓

- [ ] Code updated:
  - [ ] `main.py` imports `StaticFiles` ✓
  - [ ] `main.py` mounts frontend `/public` folder ✓
  - [ ] `App.jsx` uses `VITE_API_URL` environment variable ✓
  - [ ] `frontend/.env.example` created ✓

- [ ] Git cleaned:
  - [ ] Removed `venv/` from tracking (if accidentally committed)
  - [ ] Removed `__pycache__/` from tracking (if accidentally committed)
  - [ ] Added `.gitignore` to repository ✓

## GitHub Upload

- [ ] All files committed: `git status` shows clean working directory
- [ ] Changes pushed to GitHub: `git push origin main`
- [ ] GitHub repo reflects latest changes
  - [ ] View at https://github.com/clickcafence/data-analyzer-backend
  - [ ] Verify all new files are visible

## Frontend Build (Before Render Deployment)

Run in PowerShell at project root:

```powershell
cd frontend
npm install
npm run build
cd ..
Copy-Item -Recurse frontend/dist public -Force
git add public
git commit -m "Add built frontend for production"
git push origin main
```

- [ ] `frontend/dist/` folder created after build
- [ ] `public/` folder created at project root
- [ ] `public/index.html` exists
- [ ] `public/assets/` folder exists
- [ ] Git push successful

## Render Deployment Setup

- [ ] Render.com account created
- [ ] GitHub connected to Render
- [ ] New Web Service created
- [ ] Repository selected: `data-analyzer-backend`
- [ ] Settings configured:
  - [ ] Name: `data-analyzer-backend`
  - [ ] Environment: Python 3
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - [ ] Region: Selected (default: US)

- [ ] Web Service created
- [ ] Deployment in progress (check Logs)
- [ ] Deployment successful (URL generated)
- [ ] Live URL saved: `https://data-analyzer-backend-xxxx.onrender.com`

## Post-Deployment Testing

- [ ] Visit your live URL in browser
- [ ] Frontend loads (shows upload interface)
- [ ] Can upload CSV/Excel file
- [ ] Analysis completes without errors
- [ ] Charts display correctly
- [ ] Comparative analysis works
- [ ] No console errors (check browser DevTools)
- [ ] No API errors (check Render logs)

## Production Optimization (Optional)

- [ ] Set environment variables in Render:
  - [ ] `VITE_API_URL`: Your live backend URL (if needed)
  
- [ ] Configure custom domain (if desired)
  - [ ] Register domain
  - [ ] Add to Render settings
  - [ ] Update DNS records

- [ ] Monitor performance
  - [ ] Check Render dashboard regularly
  - [ ] Watch memory/CPU usage
  - [ ] Set up alerts (if premium)

## Maintenance Going Forward

- [ ] Regular updates pushed to GitHub
- [ ] Render auto-redeploys on git push
- [ ] Monitor logs for errors
- [ ] Test new features locally before pushing
- [ ] Keep dependencies updated (quarterly)

---

## 📊 Current Status

As of today:
- ✅ All deployment files created
- ✅ Code updated for production
- ✅ Changes pushed to GitHub
- ⏳ **Next: Build frontend and deploy to Render**

## 🎯 Final Steps (Quick)

1. **Build frontend locally** (5 minutes):
   ```powershell
   cd frontend
   npm run build
   cd ..
   Copy-Item -Recurse frontend/dist public -Force
   git add public
   git commit -m "Add built frontend for production"
   git push origin main
   ```

2. **Deploy to Render** (5 minutes):
   - Go to render.com
   - Create Web Service from GitHub
   - Use credentials above
   - Wait 2-5 minutes for deployment

3. **Test your live app** (2 minutes):
   - Visit the URL Render gives you
   - Upload a CSV file
   - Verify it works

**Total time: ~15 minutes** ⏱️

---

Last updated: 2026-01-30
