@echo off
REM Smart Kitchen Queue Management System - Windows Deployment Script

setlocal enabledelayedexpansion

REM Configuration
set DEPLOYMENT_TYPE=%1
if "%DEPLOYMENT_TYPE%"=="" set DEPLOYMENT_TYPE=development
set PROJECT_NAME=kitchen-queue-system

echo [INFO] Starting deployment of Smart Kitchen Queue Management System
echo [INFO] Deployment type: %DEPLOYMENT_TYPE%

REM Check prerequisites
echo [INFO] Checking prerequisites...

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker daemon is not running. Please start Docker first.
    exit /b 1
)

echo [SUCCESS] Prerequisites check passed

REM Setup environment
echo [INFO] Setting up environment...

if not exist .env (
    echo [INFO] Creating .env file...
    (
        echo # Smart Kitchen Queue Management System Configuration
        echo EXCEL_FILE_PATH=data/kitchen_config.xlsx
        echo OLLAMA_BASE_URL=http://ollama:11434
        echo OLLAMA_MODEL=llama2
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo DEBUG_MODE=true
        echo MAX_STARVATION_COUNT=3
        echo SYNCHRONIZATION_WINDOW_MINUTES=3
        echo PERFORMANCE_HISTORY_DAYS=30
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/kitchen_queue.log
    ) > .env
)

if not exist data mkdir data
if not exist logs mkdir logs
if not exist ssl mkdir ssl

echo [SUCCESS] Environment setup completed

REM Build application
echo [INFO] Building application...
docker-compose build --no-cache
if %errorlevel% neq 0 (
    echo [ERROR] Application build failed
    exit /b 1
)
echo [SUCCESS] Application build completed

REM Setup Ollama
echo [INFO] Setting up Ollama AI service...
docker-compose up -d ollama
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Ollama service
    exit /b 1
)

echo [INFO] Waiting for Ollama service to be ready...
set /a counter=0
:wait_ollama
curl -s http://localhost:11434/api/version >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Ollama service is ready
    goto ollama_ready
)
set /a counter+=1
if %counter% geq 30 (
    echo [ERROR] Ollama service failed to start within 30 seconds
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_ollama

:ollama_ready
echo [INFO] Downloading AI model (this may take a few minutes^)...
docker-compose exec ollama ollama pull llama2
echo [SUCCESS] Ollama setup completed

REM Deploy application
echo [INFO] Deploying application...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Application deployment failed
    exit /b 1
)

echo [INFO] Waiting for application to be ready...
set /a counter=0
:wait_app
curl -s http://localhost:8000/health >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Application is ready
    goto app_ready
)
set /a counter+=1
if %counter% geq 60 (
    echo [ERROR] Application failed to start within 60 seconds
    docker-compose logs kitchen-app
    exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_app

:app_ready
echo [SUCCESS] Application deployment completed

REM Health checks
echo [INFO] Running health checks...
curl -s http://localhost:8000/api/system/health | findstr "success.*true" >nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Application health check passed
) else (
    echo [ERROR] Application health check failed
    exit /b 1
)

curl -s http://localhost:11434/api/version >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Ollama health check passed
) else (
    echo [ERROR] Ollama health check failed
    exit /b 1
)

echo [SUCCESS] All health checks passed

REM Show deployment info
echo.
echo [SUCCESS] Deployment completed successfully!
echo.
echo === Smart Kitchen Queue Management System ===
echo Application URL: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/api/system/health
echo.
echo === Service Status ===
docker-compose ps
echo.
echo === Useful Commands ===
echo View logs: docker-compose logs -f kitchen-app
echo Stop services: docker-compose down
echo Restart services: docker-compose restart
echo Update application: deploy.bat
echo.

echo [SUCCESS] Deployment completed successfully!
exit /b 0
