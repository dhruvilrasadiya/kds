@echo off
REM Smart Kitchen Queue Management System - Windows Deployment Test Script

echo 🧪 Smart Kitchen Queue Management System - Deployment Test
echo ==========================================================

set TESTS_TOTAL=0
set TESTS_PASSED=0
set TESTS_FAILED=0

REM Test Docker services
echo 🐳 Testing Docker Services...
call :run_test "Docker Compose services running" "docker-compose ps | findstr Up"

REM Test service health
echo.
echo 🏥 Testing Service Health...
call :run_test "MongoDB health" "docker-compose exec -T mongodb mongosh --eval \"db.adminCommand('ping')\""
call :run_test "Ollama health" "curl -f http://localhost:11434/api/tags"
call :run_test "Backend health" "curl -f http://localhost:8000/health"
call :run_test "Frontend health" "curl -f http://localhost:8080/health"

REM Test API endpoints
echo.
echo 🔌 Testing API Endpoints...
call :run_test "Backend API docs" "curl -f http://localhost:8000/docs"
call :run_test "Menu items endpoint" "curl -f http://localhost:8000/api/menu/items"
call :run_test "Kitchen status endpoint" "curl -f http://localhost:8000/api/kitchens/status"

REM Test frontend
echo.
echo 🌐 Testing Frontend...
call :run_test "Frontend main page" "curl -f http://localhost:8080/"

REM Test order creation
echo.
echo 🍽️ Testing Order Creation...
curl -s -X POST http://localhost:8000/api/orders/ -H "Content-Type: application/json" -d "{\"items\": [\"1\", \"2\"], \"customer_id\": \"TEST_CUSTOMER\"}" > temp_response.json
findstr "\"success\": true" temp_response.json >nul
if %errorlevel% equ 0 (
    echo [PASS] Order creation successful
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Order creation failed
    set /a TESTS_FAILED+=1
)
set /a TESTS_TOTAL+=1
del temp_response.json 2>nul

REM Final summary
echo.
echo 📋 Test Summary
echo ===============
echo Total tests: %TESTS_TOTAL%
echo Passed: %TESTS_PASSED%
echo Failed: %TESTS_FAILED%

if %TESTS_FAILED% equ 0 (
    echo.
    echo [PASS] 🎉 All tests passed! Deployment is successful!
    echo.
    echo 🌐 Access Points:
    echo    Frontend:  http://localhost:8080
    echo    Backend:   http://localhost:8000
    echo    API Docs:  http://localhost:8000/docs
    echo.
) else (
    echo.
    echo [FAIL] ❌ Some tests failed. Please check the logs.
    echo.
    echo 🔍 Debugging commands:
    echo    docker-compose logs -f [service_name]
    echo    docker-compose ps
    echo.
)

pause
goto :eof

:run_test
set TEST_NAME=%~1
set TEST_COMMAND=%~2
set /a TESTS_TOTAL+=1

echo [TEST] %TEST_NAME%
%TEST_COMMAND% >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] %TEST_NAME%
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] %TEST_NAME%
    set /a TESTS_FAILED+=1
)
goto :eof
