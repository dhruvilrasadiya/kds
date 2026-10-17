#!/bin/bash

# Excel to MongoDB Migration Script for Linux/Mac
# Smart Kitchen Queue Management System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}📊 Excel to MongoDB Migration Tool${NC}"
    echo "===================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}🔍 $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH"
        echo "Please install Python 3.7+ and try again"
        exit 1
    fi
    
    # Use python3 if available, otherwise python
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    print_success "Python found: $($PYTHON_CMD --version)"
}

check_packages() {
    print_info "Checking required packages..."
    
    if ! $PYTHON_CMD -c "import pandas, pymongo" &> /dev/null; then
        print_warning "Required packages not found. Installing..."
        
        # Try pip3 first, then pip
        if command -v pip3 &> /dev/null; then
            pip3 install pandas openpyxl pymongo
        elif command -v pip &> /dev/null; then
            pip install pandas openpyxl pymongo
        else
            print_error "pip is not installed. Please install pip and try again"
            exit 1
        fi
        
        print_success "Packages installed successfully"
    else
        print_success "Required packages found"
    fi
}

check_excel_file() {
    if [ ! -f "data/kitchen_config.xlsx" ]; then
        print_error "Excel file not found: data/kitchen_config.xlsx"
        echo "Please ensure the Excel file exists and try again"
        exit 1
    fi
    
    print_success "Excel file found: data/kitchen_config.xlsx"
}

get_user_options() {
    echo ""
    read -p "Clear existing data? (y/N): " CLEAR_DATA
    read -p "Dry run (preview only)? (y/N): " DRY_RUN
    read -p "Use custom MongoDB URL? (y/N): " CUSTOM_MONGO
    
    COMMAND="$PYTHON_CMD excel_to_mongodb_sync.py"
    
    if [[ "$CLEAR_DATA" =~ ^[Yy]$ ]]; then
        COMMAND="$COMMAND --clear-existing"
    fi
    
    if [[ "$DRY_RUN" =~ ^[Yy]$ ]]; then
        COMMAND="$COMMAND --dry-run"
    fi
    
    if [[ "$CUSTOM_MONGO" =~ ^[Yy]$ ]]; then
        read -p "Enter MongoDB URL (default: mongodb://127.0.0.1:27017): " MONGO_URL
        if [ ! -z "$MONGO_URL" ]; then
            COMMAND="$COMMAND --mongodb-url \"$MONGO_URL\""
        fi
        
        read -p "Enter database name (default: smart_kitchen): " DB_NAME
        if [ ! -z "$DB_NAME" ]; then
            COMMAND="$COMMAND --database \"$DB_NAME\""
        fi
    fi
    
    COMMAND="$COMMAND --verbose"
}

run_migration() {
    echo ""
    print_info "Running: $COMMAND"
    echo ""
    
    if eval $COMMAND; then
        echo ""
        print_success "Migration completed successfully!"
        
        if [[ "$DRY_RUN" =~ ^[Yy]$ ]]; then
            print_info "This was a dry run. Run again without dry-run to actually migrate data."
        else
            echo -e "${GREEN}🎉 Your MongoDB database is now ready!${NC}"
        fi
    else
        echo ""
        print_error "Migration failed. Check the error messages above."
        exit 1
    fi
}

main() {
    print_header
    echo ""
    
    check_python
    check_packages
    check_excel_file
    get_user_options
    run_migration
    
    echo ""
    echo "Migration process completed."
}

# Run main function
main "$@"
