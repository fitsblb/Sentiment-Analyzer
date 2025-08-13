# 🐳 Docker Deployment Guide

This guide covers containerized deployment of the Sentiment Analyzer application.

## 📋 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/fitsblb/Sentiment-Analyzer.git
cd Sentiment-Analyzer

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker Commands

```bash
# Build the image
docker build -t fitsblb/sentiment-analyzer:latest .

# Run the container
docker run -d \
  --name sentiment-analyzer \
  -p 5000:5000 \
  --restart unless-stopped \
  fitsblb/sentiment-analyzer:latest

# View logs
docker logs -f sentiment-analyzer
```

### Using Build Scripts

**Windows:**
```cmd
# Build and run
docker-deploy.bat deploy

# Just build
docker-deploy.bat build

# Run tests
docker-deploy.bat test
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x docker-deploy.sh

# Build and run
./docker-deploy.sh deploy

# Just build
./docker-deploy.sh build

# Run tests
./docker-deploy.sh test
```

## 🏗️ Build Configuration

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs all dependencies and builds the application
2. **Production Stage**: Creates a minimal runtime image with only necessary components

### Environment Variables

Key environment variables for container configuration:

```bash
FLASK_ENV=production          # Flask environment
FLASK_DEBUG=0                 # Debug mode (0 for production)
FLASK_RUN_HOST=0.0.0.0       # Bind to all interfaces
FLASK_RUN_PORT=5000          # Application port
```

## 🔍 Health Checks

The container includes built-in health checks:

```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:5000/api/health
```

Health check endpoint returns:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-12T21:54:00Z",
  "model_status": "loaded",
  "version": "1.0.0"
}
```

## 📊 Production Deployment

### With Nginx Reverse Proxy

```bash
# Start with nginx proxy
docker-compose --profile production up -d

# Application available at:
# - Direct: http://localhost:5000
# - Through Nginx: http://localhost:80
```

### Environment Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
# Edit .env with your production values
```

### Resource Limits

For production, consider setting resource limits:

```bash
docker run -d \
  --name sentiment-analyzer \
  --memory="1g" \
  --cpus="0.5" \
  -p 5000:5000 \
  fitsblb/sentiment-analyzer:latest
```

## 🧪 Testing in Container

Run the test suite inside the container:

```bash
# Run all tests
docker run --rm fitsblb/sentiment-analyzer:latest python -m pytest tests/ -v

# Run specific test category
docker run --rm fitsblb/sentiment-analyzer:latest python -m pytest tests/test_model.py -v

# Run with coverage
docker run --rm fitsblb/sentiment-analyzer:latest python -m pytest tests/ --cov=app --cov-report=term
```

## 📈 Monitoring

### Container Logs

```bash
# Follow logs
docker logs -f sentiment-analyzer

# View recent logs
docker logs --tail 100 sentiment-analyzer

# Filter logs by level
docker logs sentiment-analyzer 2>&1 | grep ERROR
```

### Container Stats

```bash
# Resource usage
docker stats sentiment-analyzer

# Container details
docker inspect sentiment-analyzer
```

## 🔧 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs sentiment-analyzer

# Check if port is available
netstat -tulpn | grep :5000
```

**Health check failing:**
```bash
# Test health endpoint
curl -v http://localhost:5000/api/health

# Check container status
docker ps -a
```

**Model loading issues:**
```bash
# Check available disk space
docker exec sentiment-analyzer df -h

# Check model cache
docker exec sentiment-analyzer ls -la /app/model_cache/
```

### Performance Tuning

**Memory optimization:**
```bash
# Set memory limit
docker run --memory="512m" fitsblb/sentiment-analyzer:latest

# Monitor memory usage
docker stats --no-stream sentiment-analyzer
```

**CPU optimization:**
```bash
# Limit CPU usage
docker run --cpus="0.5" fitsblb/sentiment-analyzer:latest
```

## 🚀 CI/CD Integration

The repository includes GitHub Actions workflow for automated:

- ✅ Testing on push/PR
- 🔒 Security scanning
- 🐳 Docker image building
- 📦 Push to Docker Hub
- 🚀 Automated deployment

### Required Secrets

Add these secrets to your GitHub repository:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password/token

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Flask Production Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Container Security](https://docs.docker.com/engine/security/)

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review container logs: `docker logs sentiment-analyzer`
3. Verify health endpoint: `curl http://localhost:5000/api/health`
4. Open an issue on GitHub with logs and error details
