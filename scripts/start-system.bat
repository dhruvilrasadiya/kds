@echo off
REM Smart Kitchen Queue Management System - Windows Startup Script

echo 🍳 Smart Kitchen Queue Management System - Startup
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
        pause
        exit /b 1
    )
)

echo [INFO] Prerequisites check passed!

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Stop any existing containers
echo [INFO] Stopping any existing containers...
docker-compose down --remove-orphans 2>nul

REM Start infrastructure services first
echo [INFO] Starting infrastructure services...
docker-compose up -d mongodb

REM Wait for MongoDB
echo [INFO] Waiting for MongoDB to be ready...
:wait_mongodb
timeout /t 3 /nobreak >nul
docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if errorlevel 1 goto wait_mongodb
echo [SUCCESS] MongoDB is ready!


REM Start backend
echo [INFO] Starting backend service...
docker-compose up -d backend

REM Wait for backend
echo [INFO] Waiting for backend to be ready...
:wait_backend
timeout /t 2 /nobreak >nul
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 goto wait_backend
echo [SUCCESS] Backend is ready!

REM Start frontend
echo [INFO] Starting frontend service...
docker-compose up -d frontend

REM Wait for frontend
echo [INFO] Waiting for frontend to be ready...
:wait_frontend
timeout /t 2 /nobreak >nul
curl -f http://localhost:8080/health >nul 2>&1
if errorlevel 1 goto wait_frontend
echo [SUCCESS] Frontend is ready!

REM Show final status
echo.
echo 🎉 Smart Kitchen Queue Management System is now running!
echo ==================================================
echo 📱 Frontend:  http://localhost:8080
echo 🔧 Backend:   http://localhost:8000
echo 🗄️  MongoDB:   mongodb://localhost:27017
echo.
echo 📋 To view logs: docker-compose logs -f [service_name]
echo 🛑 To stop:      docker-compose down
echo.
echo [SUCCESS] System startup completed successfully!
pause
