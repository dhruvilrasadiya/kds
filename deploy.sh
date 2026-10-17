#!/bin/bash

# Smart Kitchen Queue Management System - Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_TYPE=${1:-"development"}
PROJECT_NAME="kitchen-queue-system"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env 2>/dev/null || {
            log_warning ".env.example not found, creating basic .env file"
            cat > .env << EOF
# Smart Kitchen Queue Management System Configuration
EXCEL_FILE_PATH=data/kitchen_config.xlsx
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama2
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=true
MAX_STARVATION_COUNT=3
SYNCHRONIZATION_WINDOW_MINUTES=3
PERFORMANCE_HISTORY_DAYS=30
LOG_LEVEL=INFO
LOG_FILE=logs/kitchen_queue.log
EOF
        }
    fi
    
    # Create necessary directories
    mkdir -p data logs ssl
    
    # Set appropriate permissions
    chmod 755 data logs
    
    log_success "Environment setup completed"
}

build_application() {
    log_info "Building application..."
    
    # Build Docker images
    docker-compose build --no-cache
    
    log_success "Application build completed"
}

setup_ollama() {
    log_info "Setting up Ollama AI service..."
    
    # Start Ollama service
    docker-compose up -d ollama
    
    # Wait for Ollama to be ready
    log_info "Waiting for Ollama service to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
            log_success "Ollama service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "Ollama service failed to start within 30 seconds"
            exit 1
        fi
        sleep 1
    done
    
    # Pull AI model
    log_info "Downloading AI model (this may take a few minutes)..."
    docker-compose exec ollama ollama pull llama2
    
    log_success "Ollama setup completed"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Start all services
    docker-compose up -d
    
    # Wait for application to be ready
    log_info "Waiting for application to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Application is ready"
            break
        fi
        if [ $i -eq 60 ]; then
            log_error "Application failed to start within 60 seconds"
            docker-compose logs kitchen-app
            exit 1
        fi
        sleep 1
    done
    
    log_success "Application deployment completed"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Check application health
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/system/health)
    if echo "$HEALTH_RESPONSE" | grep -q '"success": true'; then
        log_success "Application health check passed"
    else
        log_error "Application health check failed"
        echo "$HEALTH_RESPONSE"
        exit 1
    fi
    
    # Check Ollama health
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        log_success "Ollama health check passed"
    else
        log_error "Ollama health check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo
    echo "=== Smart Kitchen Queue Management System ==="
    echo "Application URL: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/api/system/health"
    echo
    echo "=== Service Status ==="
    docker-compose ps
    echo
    echo "=== Useful Commands ==="
    echo "View logs: docker-compose logs -f kitchen-app"
    echo "Stop services: docker-compose down"
    echo "Restart services: docker-compose restart"
    echo "Update application: ./deploy.sh"
    echo
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    docker-compose down
    exit 1
}

# Main deployment flow
main() {
    log_info "Starting deployment of Smart Kitchen Queue Management System"
    log_info "Deployment type: $DEPLOYMENT_TYPE"
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    # Run deployment steps
    check_prerequisites
    setup_environment
    build_application
    setup_ollama
    deploy_application
    run_health_checks
    show_deployment_info
    
    log_success "Deployment completed successfully!"
}

# Handle different deployment types
case $DEPLOYMENT_TYPE in
    "development"|"dev")
        log_info "Running development deployment"
        main
        ;;
    "production"|"prod")
        log_info "Running production deployment"
        # Override settings for production
        export DEBUG_MODE=false
        export LOG_LEVEL=WARNING
        main
        ;;
    "test")
        log_info "Running test deployment"
        # Run tests after deployment
        main
        log_info "Running tests..."
        python run_tests.py --fast
        ;;
    *)
        log_error "Invalid deployment type: $DEPLOYMENT_TYPE"
        echo "Usage: $0 [development|production|test]"
        exit 1
        ;;
esac
