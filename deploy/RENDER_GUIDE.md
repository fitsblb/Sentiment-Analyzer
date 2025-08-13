# Render Deployment Guide

## Deploy to Render

Render offers a generous free tier perfect for ML applications.

### Steps:
1. **Sign up**: Go to https://render.com and connect GitHub
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repository**: Select your `Sentiment-Analyzer` repo
4. **Configure**:
   - **Name**: sentiment-analyzer
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app/app.py`

### Settings:
- **Port**: 5000
- **Environment**: Production
- **Auto-Deploy**: On (deploys on every git push)

### Environment Variables:
```
FLASK_ENV=production
PORT=10000
```

**URL**: Your app will be available at `https://sentiment-analyzer.onrender.com`

---

## Benefits:
✅ Free 750 hours/month
✅ Automatic SSL certificates
✅ GitHub integration
✅ Custom domains on free tier
✅ No credit card required
