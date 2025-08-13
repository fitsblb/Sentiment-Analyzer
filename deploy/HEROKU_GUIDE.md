# Heroku Deployment Guide

## Deploy to Heroku

Heroku is excellent for Flask apps (no longer free, but affordable at $5/month).

### Prerequisites:
1. **Heroku Account**: Sign up at https://heroku.com
2. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli

### Required Files:

#### 1. Create `Procfile`:
```
web: python app/app.py
```

#### 2. Update requirements.txt (if needed):
```
flask==2.3.0
transformers==4.30.0
torch==2.0.0
datasets==2.12.0
requests==2.31.0
gunicorn==20.1.0
```

#### 3. Create `runtime.txt`:
```
python-3.11.4
```

### Steps:

#### 1. Login and create app:
```bash
heroku login
heroku create sentiment-analyzer-app
```

#### 2. Set environment variables:
```bash
heroku config:set FLASK_ENV=production
heroku config:set PORT=5000
```

#### 3. Deploy:
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### 4. Open app:
```bash
heroku open
```

**URL**: Your app will be available at `https://sentiment-analyzer-app.herokuapp.com`

---

## Benefits:
✅ Easy deployment
✅ Add-ons ecosystem
✅ Custom domains
✅ Professional platform
❌ No longer free ($5/month minimum)
