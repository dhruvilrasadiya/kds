@echo off
REM Excel to MongoDB Migration Script for Windows
REM Smart Kitchen Queue Management System

echo 📊 Excel to MongoDB Migration Tool
echo ====================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 🔍 Checking required packages...
python -c "import pandas, pymongo" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Required packages not found. Installing...
    pip install pandas openpyxl pymongo
    if errorlevel 1 (
        echo ❌ Failed to install required packages
        pause
        exit /b 1
    )
    echo ✅ Packages installed successfully
)

REM Check if Excel file exists
if not exist "data\kitchen_config.xlsx" (
    echo ❌ Excel file not found: data\kitchen_config.xlsx
    echo Please ensure the Excel file exists and try again
    pause
    exit /b 1
)

REM Run the migration
echo 🚀 Starting migration...
echo.

REM Ask user for options
set /p CLEAR_DATA="Clear existing data? (y/N): "
set /p DRY_RUN="Dry run (preview only)? (y/N): "

REM Build command
set COMMAND=python excel_to_mongodb_sync.py

if /i "%CLEAR_DATA%"=="y" (
    set COMMAND=%COMMAND% --clear-existing
)

if /i "%DRY_RUN%"=="y" (
    set COMMAND=%COMMAND% --dry-run
)

set COMMAND=%COMMAND% --verbose

REM Execute migration
echo.
echo 📋 Running: %COMMAND%
echo.
%COMMAND%

if errorlevel 1 (
    echo.
    echo ❌ Migration failed. Check the error messages above.
) else (
    echo.
    echo ✅ Migration completed successfully!
    if /i "%DRY_RUN%"=="y" (
        echo 🔍 This was a dry run. Run again without dry-run to actually migrate data.
    ) else (
        echo 🎉 Your MongoDB database is now ready!
    )
)

echo.
pause
