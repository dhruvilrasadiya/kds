#!/bin/bash

# Smart Kitchen Queue Management System - Stop Script
# This script gracefully stops all services

set -e

echo "🛑 Smart Kitchen Queue Management System - Shutdown"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Parse command line arguments
REMOVE_VOLUMES=false
REMOVE_IMAGES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --remove-volumes)
            REMOVE_VOLUMES=true
            shift
            ;;
        --remove-images)
            REMOVE_IMAGES=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --remove-volumes    Remove all volumes (WARNING: This will delete all data!)"
            echo "  --remove-images     Remove built images"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Stop services gracefully
print_status "Stopping services gracefully..."
docker-compose stop

# Remove containers
print_status "Removing containers..."
docker-compose down --remove-orphans

if [ "$REMOVE_VOLUMES" = true ]; then
    print_warning "Removing volumes (this will delete all data)..."
    docker-compose down -v
    print_warning "All data has been removed!"
fi

if [ "$REMOVE_IMAGES" = true ]; then
    print_status "Removing built images..."
    docker-compose down --rmi local
fi

# Clean up any dangling containers or networks
print_status "Cleaning up..."
docker system prune -f >/dev/null 2>&1 || true

print_success "System shutdown completed!"

if [ "$REMOVE_VOLUMES" = false ]; then
    echo ""
    echo "📋 Data has been preserved in Docker volumes"
    echo "🔄 To restart: ./scripts/start-system.sh"
    echo "🗑️  To remove all data: $0 --remove-volumes"
fi
