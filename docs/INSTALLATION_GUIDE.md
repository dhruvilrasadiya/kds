# Smart Kitchen Queue Management System - Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: At least 1GB free space
- **Network**: Internet connection for initial setup and AI model downloads

### Required Software
1. **Python 3.8+** with pip
2. **Ollama** (for AI functionality)
3. **Git** (for version control)

## Installation Steps

### 1. Install Ollama

#### Windows
1. Download Ollama from [https://ollama.ai](https://ollama.ai)
2. Run the installer and follow the setup wizard
3. Open Command Prompt and verify installation:
```cmd
ollama --version
```

#### macOS
```bash
# Using Homebrew
brew install ollama

# Or download from https://ollama.ai
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Download AI Model
```bash
# Download the default model (llama2)
ollama pull llama2

# Or use a different model (optional)
ollama pull codellama
```

### 3. Clone the Repository
```bash
git clone <repository-url>
cd kds
```

### 4. Set Up Python Environment

#### Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configuration

#### Environment Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your settings:
```env
# Excel Configuration
EXCEL_FILE_PATH=data/kitchen_config.xlsx

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=True

# Kitchen Configuration
MAX_STARVATION_COUNT=3
SYNCHRONIZATION_WINDOW_MINUTES=3
PERFORMANCE_HISTORY_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/kitchen_queue.log
```

#### Excel Configuration
The system will automatically create a sample Excel configuration file on first run. You can customize it by editing `data/kitchen_config.xlsx` with your specific:
- Kitchen configurations
- Menu items
- Historical performance data
- Load patterns

### 6. Initialize the System

#### Create Sample Data
```bash
python -c "from app.utils.excel_creator import create_sample_excel; create_sample_excel('data/kitchen_config.xlsx')"
```

#### Test Installation
```bash
python -m pytest tests/ -v
```

### 7. Start the System

#### Start Ollama Service
```bash
# Make sure Ollama is running
ollama serve
```

#### Start the Application
```bash
python main.py
```

The system will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/system/health

## Verification

### 1. Check System Health
```bash
curl http://localhost:8000/api/system/health
```

Expected response:
```json
{
  "success": true,
  "status": "healthy",
  "components": {
    "excel_service": "healthy - 3 kitchens loaded",
    "queue_manager": "healthy - 0 items in queues",
    "ai_agent": "healthy - agent initialized"
  }
}
```

### 2. Test Order Creation
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"items": ["ITM_001", "ITM_004"]}'
```

### 3. View Kitchen Status
```bash
curl http://localhost:8000/api/kitchens/status
```

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
**Error**: `Connection refused to Ollama service`
**Solution**:
- Ensure Ollama is running: `ollama serve`
- Check Ollama URL in `.env` file
- Verify firewall settings

#### 2. Excel File Not Found
**Error**: `Excel file not found`
**Solution**:
- Run the Excel creator script
- Check file path in `.env` configuration
- Ensure proper file permissions

#### 3. Port Already in Use
**Error**: `Port 8000 already in use`
**Solution**:
- Change `API_PORT` in `.env` file
- Kill existing process: `lsof -ti:8000 | xargs kill -9` (macOS/Linux)

#### 4. Memory Issues
**Error**: `Out of memory`
**Solution**:
- Increase system RAM
- Use a smaller AI model
- Reduce `PERFORMANCE_HISTORY_DAYS` setting

#### 5. Permission Errors
**Error**: `Permission denied`
**Solution**:
- Run with appropriate permissions
- Check file/directory ownership
- Ensure write access to logs directory

### Performance Optimization

#### 1. AI Model Selection
- **llama2**: Good balance of performance and accuracy
- **codellama**: Better for code-related tasks
- **mistral**: Faster inference, lower memory usage

#### 2. System Tuning
```env
# For better performance
MAX_STARVATION_COUNT=2
SYNCHRONIZATION_WINDOW_MINUTES=2
PERFORMANCE_HISTORY_DAYS=7
```

#### 3. Hardware Recommendations
- **CPU**: Multi-core processor (4+ cores recommended)
- **RAM**: 8GB+ for optimal AI performance
- **Storage**: SSD for faster data access

## Development Setup

### Additional Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Code Quality Tools
```bash
# Install development tools
pip install flake8 black pytest-cov

# Run code formatting
black app/ tests/

# Run linting
flake8 app/ --max-line-length=100

# Run tests with coverage
pytest --cov=app tests/
```

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## Docker Setup (Optional)

### Build Docker Image
```bash
docker build -t kitchen-queue-system .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Next Steps

1. **Customize Configuration**: Edit Excel files for your specific kitchen setup
2. **Set Up Monitoring**: Configure logging and monitoring systems
3. **Security**: Implement authentication and authorization
4. **Scaling**: Consider load balancing for high-traffic scenarios
5. **Backup**: Set up regular backups of configuration and historical data

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review system logs in `logs/kitchen_queue.log`
3. Run health checks to identify component issues
4. Consult the API documentation for usage examples
