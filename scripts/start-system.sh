#!/bin/bash

# Smart Kitchen Queue Management System - Startup Script
# This script starts the entire system with proper initialization

set -e

echo "🍳 Smart Kitchen Queue Management System - Startup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Prerequisites check passed!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data logs scripts

# Ensure data files exist
if [ ! -f "data/kitchen_config.xlsx" ]; then
    print_warning "Excel configuration file not found. The system will create a default one."
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
print_warning "This may take several minutes on first run..."

# Start infrastructure services first (MongoDB, Ollama)
print_status "Starting infrastructure services..."
docker-compose up -d mongodb ollama

# Wait for MongoDB to be ready
print_status "Waiting for MongoDB to be ready..."
timeout=60
counter=0
until docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "MongoDB failed to start within $timeout seconds"
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_success "MongoDB is ready!"

# Wait for Ollama to be ready
print_status "Waiting for Ollama to be ready..."
timeout=120
counter=0
until curl -f http://localhost:11434/api/tags >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Ollama failed to start within $timeout seconds"
        exit 1
    fi
    sleep 3
    counter=$((counter + 3))
    echo -n "."
done
echo ""
print_success "Ollama is ready!"

# Download required model if not present
print_status "Checking Ollama model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.1:8b"; then
    print_warning "Required model not found. Downloading llama3.1:8b..."
    print_warning "This may take 10-20 minutes depending on your internet connection..."
    
    curl -X POST http://localhost:11434/api/pull \
        -H "Content-Type: application/json" \
        -d '{"name": "llama3.1:8b"}' \
        --max-time 1800 || {
        print_error "Failed to download model. You can download it manually later."
    }
fi

# Start backend service
print_status "Starting backend service..."
docker-compose up -d backend

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
timeout=60
counter=0
until curl -f http://localhost:8000/health >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_success "Backend is ready!"

# Start frontend service
print_status "Starting frontend service..."
docker-compose up -d frontend

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
timeout=60
counter=0
until curl -f http://localhost:8080/health >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        docker-compose logs frontend
        exit 1
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done
echo ""
print_success "Frontend is ready!"

# Final status check
print_status "Performing final system check..."
docker-compose ps

echo ""
echo "🎉 Smart Kitchen Queue Management System is now running!"
echo "=================================================="
echo "📱 Frontend:  http://localhost:8080"
echo "🔧 Backend:   http://localhost:8000"
echo "🧠 Ollama:    http://localhost:11434"
echo "🗄️  MongoDB:   mongodb://localhost:27017"
echo ""
echo "📋 To view logs: docker-compose logs -f [service_name]"
echo "🛑 To stop:      docker-compose down"
echo "🔄 To restart:   docker-compose restart [service_name]"
echo ""
print_success "System startup completed successfully!"
