#!/bin/bash

# Docker build and deployment scripts for Sentiment Analyzer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="fitsblb/sentiment-analyzer"
CONTAINER_NAME="sentiment-analyzer-app"

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to build Docker image
build_image() {
    local tag=${1:-latest}
    print_step "Building Docker image: $IMAGE_NAME:$tag"
    
    docker build -t "$IMAGE_NAME:$tag" . || {
        print_error "Failed to build Docker image"
        exit 1
    }
    
    print_success "Docker image built successfully: $IMAGE_NAME:$tag"
}

# Function to run container
run_container() {
    local tag=${1:-latest}
    local port=${2:-5000}
    
    print_step "Running container on port $port"
    
    # Stop existing container if running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_warning "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1
    fi
    
    # Run new container
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$port:5000" \
        --restart unless-stopped \
        "$IMAGE_NAME:$tag" || {
        print_error "Failed to run container"
        exit 1
    }
    
    print_success "Container is running at http://localhost:$port"
    
    # Wait for health check
    print_step "Waiting for application to be ready..."
    for i in {1..30}; do
        if curl -s "http://localhost:$port/api/health" >/dev/null 2>&1; then
            print_success "Application is healthy!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Application failed to start within 30 seconds"
            docker logs "$CONTAINER_NAME"
            exit 1
        fi
        sleep 1
    done
}

# Function to push to registry
push_image() {
    local tag=${1:-latest}
    print_step "Pushing image to Docker Hub: $IMAGE_NAME:$tag"
    
    docker push "$IMAGE_NAME:$tag" || {
        print_error "Failed to push image"
        exit 1
    }
    
    print_success "Image pushed successfully: $IMAGE_NAME:$tag"
}

# Function to run tests in container
test_container() {
    local tag=${1:-latest}
    print_step "Running tests in container"
    
    docker run --rm \
        "$IMAGE_NAME:$tag" \
        python -m pytest tests/ -v || {
        print_error "Tests failed in container"
        exit 1
    }
    
    print_success "All tests passed in container"
}

# Function to show logs
show_logs() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        print_step "Showing container logs"
        docker logs -f "$CONTAINER_NAME"
    else
        print_error "Container $CONTAINER_NAME is not running"
        exit 1
    fi
}

# Function to clean up
cleanup() {
    print_step "Cleaning up Docker resources"
    
    # Stop and remove container
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1
        print_success "Container removed"
    fi
    
    # Remove unused images
    docker image prune -f >/dev/null 2>&1
    print_success "Cleanup completed"
}

# Main script logic
case "$1" in
    "build")
        build_image "$2"
        ;;
    "run")
        build_image "$2"
        run_container "$2" "$3"
        ;;
    "push")
        push_image "$2"
        ;;
    "test")
        test_container "$2"
        ;;
    "logs")
        show_logs
        ;;
    "cleanup")
        cleanup
        ;;
    "deploy")
        build_image "$2"
        test_container "$2"
        run_container "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {build|run|push|test|logs|cleanup|deploy} [tag] [port]"
        echo ""
        echo "Commands:"
        echo "  build [tag]        - Build Docker image (default: latest)"
        echo "  run [tag] [port]   - Build and run container (default: latest, 5000)"
        echo "  push [tag]         - Push image to Docker Hub (default: latest)"
        echo "  test [tag]         - Run tests in container (default: latest)"
        echo "  logs               - Show container logs"
        echo "  cleanup            - Stop container and clean up"
        echo "  deploy [tag] [port] - Build, test, and run (default: latest, 5000)"
        echo ""
        echo "Examples:"
        echo "  $0 build v1.0"
        echo "  $0 run latest 8080"
        echo "  $0 deploy v1.0 5000"
        exit 1
        ;;
esac
