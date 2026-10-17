@echo off
REM Smart Kitchen Queue Management System - Windows Stop Script

echo 🛑 Smart Kitchen Queue Management System - Shutdown
echo ==================================================

REM Parse command line arguments
set REMOVE_VOLUMES=false
set REMOVE_IMAGES=false

:parse_args
if "%1"=="--remove-volumes" (
    set REMOVE_VOLUMES=true
    shift
    goto parse_args
)
if "%1"=="--remove-images" (
    set REMOVE_IMAGES=true
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo.
    echo Options:
    echo   --remove-volumes    Remove all volumes ^(WARNING: This will delete all data!^)
    echo   --remove-images     Remove built images
    echo   --help             Show this help message
    exit /b 0
)
if not "%1"=="" (
    echo Unknown option: %1
    echo Use --help for usage information
    exit /b 1
)

REM Stop services gracefully
echo [INFO] Stopping services gracefully...
docker-compose stop

REM Remove containers
echo [INFO] Removing containers...
docker-compose down --remove-orphans

if "%REMOVE_VOLUMES%"=="true" (
    echo [WARNING] Removing volumes ^(this will delete all data^)...
    docker-compose down -v
    echo [WARNING] All data has been removed!
)

if "%REMOVE_IMAGES%"=="true" (
    echo [INFO] Removing built images...
    docker-compose down --rmi local
)

REM Clean up
echo [INFO] Cleaning up...
docker system prune -f >nul 2>&1

echo [SUCCESS] System shutdown completed!

if "%REMOVE_VOLUMES%"=="false" (
    echo.
    echo 📋 Data has been preserved in Docker volumes
    echo 🔄 To restart: scripts\start-system.bat
    echo 🗑️  To remove all data: %0 --remove-volumes
)

pause
