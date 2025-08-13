# Google Cloud Run Deployment Guide

## Deploy to Google Cloud Run

Cloud Run offers excellent free tier and scales automatically.

### Prerequisites:
1. **Google Cloud Account** (free $300 credit for new users)
2. **Google Cloud CLI** installed

### Steps:

#### 1. Setup Google Cloud:
```bash
# Install Google Cloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Login and setup project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 2. Create Cloud Run configuration:
Create `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/sentiment-analyzer', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/sentiment-analyzer']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: ['run', 'deploy', 'sentiment-analyzer', 
           '--image', 'gcr.io/$PROJECT_ID/sentiment-analyzer',
           '--platform', 'managed',
           '--region', 'us-central1',
           '--allow-unauthenticated']
```

#### 3. Deploy:
```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml .

# Or direct deploy (simpler):
gcloud run deploy sentiment-analyzer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**URL**: Your app will be available at `https://sentiment-analyzer-xxx.run.app`

---

## Benefits:
✅ 2M requests/month free
✅ Auto-scaling (scales to 0 when not used)
✅ Production-grade infrastructure
✅ Custom domains
✅ HTTPS by default
✅ Perfect for ML models
