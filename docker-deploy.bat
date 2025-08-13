@echo off
REM Docker build and deployment scripts for Sentiment Analyzer (Windows)

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=fitsblb/sentiment-analyzer
set CONTAINER_NAME=sentiment-analyzer-app

REM Function to print colored output (Windows)
echo [96m🚀 Sentiment Analyzer Docker Manager[0m
echo.

if "%1"=="" goto usage

if "%1"=="build" goto build
if "%1"=="run" goto run
if "%1"=="push" goto push
if "%1"=="test" goto test
if "%1"=="logs" goto logs
if "%1"=="cleanup" goto cleanup
if "%1"=="deploy" goto deploy
goto usage

:build
echo [94m🔄 Building Docker image...[0m
set tag=%2
if "%tag%"=="" set tag=latest

docker build -t %IMAGE_NAME%:%tag% . || (
    echo [91m❌ Failed to build Docker image[0m
    exit /b 1
)

echo [92m✅ Docker image built successfully: %IMAGE_NAME%:%tag%[0m
goto end

:run
echo [94m🔄 Running container...[0m
set tag=%2
if "%tag%"=="" set tag=latest
set port=%3
if "%port%"=="" set port=5000

REM Stop existing container if running
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if !errorlevel! equ 0 (
    echo [93m⚠️  Stopping existing container: %CONTAINER_NAME%[0m
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
)

REM Run new container
docker run -d --name %CONTAINER_NAME% -p %port%:5000 --restart unless-stopped %IMAGE_NAME%:%tag% || (
    echo [91m❌ Failed to run container[0m
    exit /b 1
)

echo [92m✅ Container is running at http://localhost:%port%[0m

REM Wait for health check
echo [94m🔄 Waiting for application to be ready...[0m
for /l %%i in (1,1,30) do (
    curl -s http://localhost:%port%/api/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo [92m✅ Application is healthy![0m
        goto end
    )
    timeout /t 1 >nul
)

echo [91m❌ Application failed to start within 30 seconds[0m
docker logs %CONTAINER_NAME%
exit /b 1

:push
echo [94m🔄 Pushing image to Docker Hub...[0m
set tag=%2
if "%tag%"=="" set tag=latest

docker push %IMAGE_NAME%:%tag% || (
    echo [91m❌ Failed to push image[0m
    exit /b 1
)

echo [92m✅ Image pushed successfully: %IMAGE_NAME%:%tag%[0m
goto end

:test
echo [94m🔄 Running tests in container...[0m
set tag=%2
if "%tag%"=="" set tag=latest

docker run --rm %IMAGE_NAME%:%tag% python -m pytest tests/ -v || (
    echo [91m❌ Tests failed in container[0m
    exit /b 1
)

echo [92m✅ All tests passed in container[0m
goto end

:logs
echo [94m🔄 Showing container logs...[0m
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if !errorlevel! neq 0 (
    echo [91m❌ Container %CONTAINER_NAME% is not running[0m
    exit /b 1
)

docker logs -f %CONTAINER_NAME%
goto end

:cleanup
echo [94m🔄 Cleaning up Docker resources...[0m

REM Stop and remove container
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if !errorlevel! equ 0 (
    docker stop %CONTAINER_NAME% >nul 2>&1
    docker rm %CONTAINER_NAME% >nul 2>&1
    echo [92m✅ Container removed[0m
)

REM Remove unused images
docker image prune -f >nul 2>&1
echo [92m✅ Cleanup completed[0m
goto end

:deploy
echo [94m🔄 Deploying application...[0m
call %0 build %2
if !errorlevel! neq 0 exit /b 1

call %0 test %2
if !errorlevel! neq 0 exit /b 1

call %0 run %2 %3
goto end

:usage
echo Usage: %0 {build^|run^|push^|test^|logs^|cleanup^|deploy} [tag] [port]
echo.
echo Commands:
echo   build [tag]        - Build Docker image (default: latest)
echo   run [tag] [port]   - Build and run container (default: latest, 5000)
echo   push [tag]         - Push image to Docker Hub (default: latest)
echo   test [tag]         - Run tests in container (default: latest)
echo   logs               - Show container logs
echo   cleanup            - Stop container and clean up
echo   deploy [tag] [port] - Build, test, and run (default: latest, 5000)
echo.
echo Examples:
echo   %0 build v1.0
echo   %0 run latest 8080
echo   %0 deploy v1.0 5000

:end
