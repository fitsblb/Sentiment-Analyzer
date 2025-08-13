# Railway Deployment Guide

## Deploy to Railway (Recommended)

Railway offers the easiest deployment for Flask apps with generous free tier.

### Steps:
1. **Sign up**: Go to https://railway.app and sign up with GitHub
2. **New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Select Repository**: Choose your `Sentiment-Analyzer` repo
4. **Auto Deploy**: Railway will automatically detect your Flask app

### Configuration:
Railway will automatically:
- Detect your `requirements.txt`
- Build and deploy your Flask app
- Provide a public URL

### Environment Variables (if needed):
- `FLASK_ENV=production`
- `PORT=5000` (Railway handles this automatically)

### Custom Start Command:
```bash
python app/app.py
```

**URL**: Your app will be available at `https://your-app-name.railway.app`

---

## Benefits:
✅ Free 500 hours/month (enough for demo/portfolio)
✅ Automatic HTTPS
✅ Custom domains
✅ GitHub integration
✅ Zero configuration
✅ Supports ML models
