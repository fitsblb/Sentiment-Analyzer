# 🛠️ Docker Troubleshooting Guide

## 🚨 Common Docker Build Issues & Solutions

### **Issue 1: Insufficient System Resources**
```
ERROR: failed to solve: rpc error: code = Unknown desc = Insufficient system resources
```

**Solutions:**
```bash
# 1. Clean up Docker resources
docker system prune -f
docker builder prune -f

# 2. Increase Docker Desktop memory limit
# Docker Desktop → Settings → Resources → Memory → Increase to 4GB+

# 3. Close other applications to free up RAM

# 4. Check available disk space
docker system df
```

### **Issue 2: Large Build Context**
```
transferring context: 963.50MB
```

**Solutions:**
```bash
# 1. Check .dockerignore file includes:
venv/
__pycache__/
*.pyc
.git/
node_modules/

# 2. Verify context size
docker build --dry-run .

# 3. Use .dockerignore effectively
echo "unwanted-large-folder/" >> .dockerignore
```

### **Issue 3: Model Loading Failures**
```
ModuleNotFoundError: No module named 'torch'
```

**Solutions:**
```bash
# 1. Check requirements.txt includes all dependencies
# 2. Use CPU-only PyTorch for smaller images:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Verify Python path in container
docker run -it fitsblb/sentiment-analyzer:latest python -c "import sys; print(sys.path)"
```

### **Issue 4: Container Won't Start**
```
Container exits immediately
```

**Solutions:**
```bash
# 1. Check container logs
docker logs container-name

# 2. Run container interactively
docker run -it fitsblb/sentiment-analyzer:latest /bin/bash

# 3. Test health endpoint
curl http://localhost:5000/api/health

# 4. Check port conflicts
netstat -tulpn | grep :5000
```

### **Issue 5: Build Cache Problems**
```
Layer cache is corrupted
```

**Solutions:**
```bash
# 1. Build without cache
docker build --no-cache -t fitsblb/sentiment-analyzer:latest .

# 2. Clean build cache
docker builder prune -f

# 3. Reset Docker Desktop (last resort)
# Docker Desktop → Settings → Reset to factory defaults
```

## ⚡ Quick Fixes

### **Free Up Space**
```bash
# Remove all stopped containers
docker container prune -f

# Remove unused images
docker image prune -f

# Remove everything unused
docker system prune -af
```

### **Optimize Build**
```bash
# Use smaller base image
FROM python:3.11-alpine  # Instead of python:3.11

# Multi-stage build for smaller final image
FROM python:3.11 as builder
# ... build steps
FROM python:3.11-slim as production
COPY --from=builder /app /app
```

### **Memory Management**
```bash
# Limit container memory
docker run -m 512m fitsblb/sentiment-analyzer:latest

# Check memory usage
docker stats container-name
```

## 🔍 Debugging Commands

```bash
# Inspect image layers
docker history fitsblb/sentiment-analyzer:latest

# Check image size
docker images fitsblb/sentiment-analyzer

# Inspect container
docker inspect container-name

# Execute into running container
docker exec -it container-name /bin/bash

# View real-time logs
docker logs -f container-name
```

## 📊 Performance Optimization

### **Reduce Image Size**
1. Use slim/alpine base images
2. Multi-stage builds
3. Remove development dependencies in production
4. Clean up package caches

### **Faster Builds**
1. Order Dockerfile commands by change frequency
2. Use .dockerignore effectively  
3. Leverage layer caching
4. Use BuildKit for parallel builds

### **Runtime Optimization**
1. Set resource limits
2. Use health checks
3. Configure proper restart policies
4. Monitor container metrics

## 🆘 Emergency Recovery

If Docker becomes completely unresponsive:

```bash
# Windows
# 1. Restart Docker Desktop
# 2. Run as Administrator: docker system prune -af
# 3. Increase VM memory in Docker Desktop settings
# 4. Restart computer if necessary

# Linux
sudo systemctl restart docker
sudo docker system prune -af
```

Remember: **Docker issues are usually related to resources (memory/disk) or context size!**
