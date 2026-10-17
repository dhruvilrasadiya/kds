#!/bin/bash

# Smart Kitchen Queue Management System - Deployment Test Script
# This script tests all services and endpoints after deployment

set -e

echo "🧪 Smart Kitchen Queue Management System - Deployment Test"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    print_test "$test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        print_pass "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_fail "$test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test Docker services
echo "🐳 Testing Docker Services..."
run_test "Docker Compose services running" "docker-compose ps | grep -q 'Up'"

# Test individual service health
echo ""
echo "🏥 Testing Service Health..."
run_test "MongoDB health check" "docker-compose exec -T mongodb mongosh --eval 'db.adminCommand(\"ping\")'"
run_test "Ollama health check" "curl -f http://localhost:11434/api/tags"
run_test "Backend health check" "curl -f http://localhost:8000/health"
run_test "Frontend health check" "curl -f http://localhost:8080/health"

# Test API endpoints
echo ""
echo "🔌 Testing API Endpoints..."
run_test "Backend API documentation" "curl -f http://localhost:8000/docs"
run_test "Backend API OpenAPI spec" "curl -f http://localhost:8000/openapi.json"
run_test "Menu items endpoint" "curl -f http://localhost:8000/api/menu/items"
run_test "Kitchen status endpoint" "curl -f http://localhost:8000/api/kitchens/status"

# Test frontend accessibility
echo ""
echo "🌐 Testing Frontend..."
run_test "Frontend main page" "curl -f http://localhost:8080/"
run_test "Frontend static assets" "curl -f http://localhost:8080/favicon.ico"

# Test database connectivity
echo ""
echo "🗄️ Testing Database..."
run_test "MongoDB connection" "docker-compose exec -T mongodb mongosh --eval 'db.runCommand({connectionStatus: 1})'"
run_test "Database collections" "docker-compose exec -T mongodb mongosh smart_kitchen --eval 'db.getCollectionNames()'"

# Test AI service
echo ""
echo "🧠 Testing AI Service..."
run_test "Ollama model availability" "curl -s http://localhost:11434/api/tags | grep -q 'llama'"
if run_test "Ollama simple generation" "curl -X POST http://localhost:11434/api/generate -H 'Content-Type: application/json' -d '{\"model\": \"llama3.1:8b\", \"prompt\": \"Hello\", \"stream\": false}' --max-time 30"; then
    print_pass "AI service is functional"
else
    print_warn "AI service may need model download"
fi

# Test order creation (integration test)
echo ""
echo "🍽️ Testing Order Creation..."
ORDER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/ \
    -H "Content-Type: application/json" \
    -d '{"items": ["1", "2"], "customer_id": "TEST_CUSTOMER"}' \
    --max-time 30)

if echo "$ORDER_RESPONSE" | grep -q '"success": true'; then
    print_pass "Order creation successful"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_fail "Order creation failed"
    echo "Response: $ORDER_RESPONSE"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Performance tests
echo ""
echo "⚡ Testing Performance..."
FRONTEND_RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8080/)
BACKEND_RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)

echo "Frontend response time: ${FRONTEND_RESPONSE_TIME}s"
echo "Backend response time: ${BACKEND_RESPONSE_TIME}s"

if (( $(echo "$FRONTEND_RESPONSE_TIME < 2.0" | bc -l) )); then
    print_pass "Frontend response time acceptable"
else
    print_warn "Frontend response time slow (${FRONTEND_RESPONSE_TIME}s)"
fi

if (( $(echo "$BACKEND_RESPONSE_TIME < 1.0" | bc -l) )); then
    print_pass "Backend response time acceptable"
else
    print_warn "Backend response time slow (${BACKEND_RESPONSE_TIME}s)"
fi

# Resource usage check
echo ""
echo "📊 Resource Usage..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -5

# Final summary
echo ""
echo "📋 Test Summary"
echo "==============="
echo "Total tests: $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    print_pass "🎉 All tests passed! Deployment is successful!"
    echo ""
    echo "🌐 Access Points:"
    echo "   Frontend:  http://localhost:8080"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo ""
    print_fail "❌ Some tests failed. Please check the logs and fix issues."
    echo ""
    echo "🔍 Debugging commands:"
    echo "   docker-compose logs -f [service_name]"
    echo "   docker-compose ps"
    echo "   docker-compose exec [service_name] /bin/sh"
    echo ""
    exit 1
fi
