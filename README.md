# Smart Kitchen Queue Management System

An intelligent kitchen queue management system that optimizes food preparation across multiple kitchens using AI-driven prioritization with anti-starvation mechanisms and real-time learning capabilities.

## 🚀 Features

### Core Functionality
- **AI-Driven Scheduling**: Uses Ollama LLM with custom LangChain tools for intelligent order prioritization
- **Multi-Kitchen Support**: Manages 3 specialized kitchens (Grill, Pasta, Dessert) with different capacities
- **Anti-Starvation System**: Prevents items from being perpetually delayed with emergency priority mechanisms
- **Historical Learning**: Continuously learns from past performance to improve future scheduling decisions
- **Real-time Updates**: Provides live status updates and automatic queue management
- **Excel Configuration**: Easy configuration and data management through Excel spreadsheets

### Advanced Features
- **Synchronization**: Ensures order items complete within 2-3 minutes of each other
- **Performance Analytics**: Comprehensive metrics and bottleneck identification
- **Emergency Rescheduling**: Automatic intervention for starving items
- **Capacity Management**: Intelligent load balancing across kitchen resources
- **RESTful API**: Complete API with FastAPI and automatic documentation

## 🏗️ Architecture

### Technology Stack
- **AI Layer**: Ollama + LangChain (Local LLM with custom tools)
- **Backend**: FastAPI (Python) with Pydantic models
- **Data Management**: Excel + Pandas for configuration and historical data
- **Queue Management**: In-memory with persistent logging and real-time updates
- **Testing**: Comprehensive test suite with pytest
- **Deployment**: Docker + Docker Compose with production-ready configuration

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   AI Agent       │    │   Kitchen       │
│   Backend       │◄──►│   (Ollama +      │◄──►│   Queue         │
│                 │    │   LangChain)     │    │   Manager       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Excel Data    │    │   Performance    │    │   Starvation    │
│   Service       │    │   Learning       │    │   Prevention    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

**Prerequisites:**
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- 8GB+ RAM (16GB recommended for AI features)

```bash
# Clone the repository
git clone <repository-url>
cd smart-kitchen-queue-system

# Start the entire system (Windows)
scripts\start-system.bat

# Start the entire system (Linux/Mac)
chmod +x scripts/*.sh
./scripts/start-system.sh

# Test deployment
./scripts/test-deployment.sh
```

**Access Points:**
- 🌐 **Frontend**: http://localhost:8080
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🧠 **Ollama AI**: http://localhost:11434

**Management Commands:**
```bash
# Stop system
./scripts/stop-system.sh

# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart [service_name]
```

### Option 2: Manual Development Setup

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- MongoDB (optional, falls back to Excel)
- Ollama (for AI features)

1. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Setup Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai)
   ollama serve
   ollama pull llama3.1:8b
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the Application**
   ```bash
   # Start backend
   python -m uvicorn app.main:app --reload

   # Start frontend (in another terminal)
   cd frontend
   npm run dev
   ```

### Access Points
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/system/health

## 📁 Project Structure

```
kds/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── models/                      # Pydantic data models
│   │   ├── __init__.py
│   │   ├── base.py                  # Core models (Order, QueueItem, etc.)
│   │   ├── enums.py                 # Status enumerations
│   │   ├── requests.py              # API request models
│   │   └── responses.py             # API response models
│   ├── services/                    # Business logic services
│   │   ├── __init__.py
│   │   ├── excel_service.py         # Excel data management
│   │   ├── queue_manager.py         # Kitchen queue operations
│   │   ├── starvation_prevention.py # Anti-starvation system
│   │   ├── ai_agent.py              # AI scheduling agent
│   │   ├── ai_tools.py              # LangChain AI tools
│   │   ├── performance_learning.py  # Learning system
│   │   └── realtime_updater.py      # Real-time updates
│   ├── api/                         # API endpoints
│   │   ├── __init__.py
│   │   ├── orders.py                # Order management endpoints
│   │   ├── kitchens.py              # Kitchen management endpoints
│   │   ├── realtime.py              # Real-time endpoints
│   │   └── system.py                # System management endpoints
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       └── excel_creator.py         # Sample Excel file creator
├── data/
│   └── kitchen_config.xlsx          # Kitchen and menu configuration
├── tests/                           # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration and fixtures
│   ├── test_excel_service.py        # Excel service tests
│   ├── test_queue_manager.py        # Queue manager tests
│   ├── test_starvation_prevention.py # Anti-starvation tests
│   ├── test_integration.py          # Integration tests
│   ├── test_api.py                  # API endpoint tests
│   └── test_performance.py          # Performance tests
├── docs/                            # Documentation
│   ├── API_DOCUMENTATION.md         # Complete API reference
│   ├── INSTALLATION_GUIDE.md        # Installation instructions
│   ├── DEPLOYMENT_GUIDE.md          # Deployment guide
│   └── USER_GUIDE.md                # User manual
├── logs/                            # Application logs
├── docker-compose.yml               # Docker deployment configuration
├── Dockerfile                       # Docker image configuration
├── nginx.conf                       # Nginx reverse proxy configuration
├── deploy.sh                        # Linux/macOS deployment script
├── deploy.bat                       # Windows deployment script
├── run_tests.py                     # Test runner script
├── requirements.txt                 # Python dependencies
├── .env                            # Environment configuration
├── .gitignore                      # Git ignore rules
├── main.py                         # Application entry point
└── README.md                       # This file
```

## 🔧 API Endpoints

### Order Management
- `POST /api/orders/` - Submit new order with AI optimization
- `GET /api/orders/{order_id}` - Get order status and details
- `GET /api/orders/` - List orders with filtering
- `PUT /api/orders/{order_id}` - Update order
- `PUT /api/orders/{order_id}/cancel` - Cancel order

### Kitchen Management
- `GET /api/kitchens/status` - Get all kitchen statuses
- `GET /api/kitchens/{kitchen_id}` - Get specific kitchen status
- `PUT /api/kitchens/{kitchen_id}/complete/{item_id}` - Mark item as completed
- `PUT /api/kitchens/{kitchen_id}/start/{item_id}` - Start item preparation
- `GET /api/kitchens/{kitchen_id}/efficiency` - Get kitchen efficiency metrics

### Real-time Operations
- `GET /api/realtime/queue` - Get current queue status
- `GET /api/realtime/performance` - Get performance metrics
- `POST /api/realtime/performance/history` - Query historical data
- `GET /api/realtime/starvation` - Get starvation status
- `POST /api/realtime/reoptimize` - Trigger AI reoptimization
- `POST /api/realtime/emergency-reschedule` - Emergency rescheduling

### System Management
- `GET /api/system/health` - Comprehensive health check
- `POST /api/system/reload-config` - Reload configuration
- `GET /api/system/metrics` - System metrics
- `GET /api/system/learning-report` - AI learning report
- `GET /api/system/config` - Current configuration

## ⚙️ Configuration

### Excel-Based Configuration
The system uses `data/kitchen_config.xlsx` with four sheets:

1. **kitchens** - Kitchen configurations (ID, name, capacity, specialization)
2. **items** - Menu items (ID, name, kitchen assignment, prep time, difficulty)
3. **historical_performance** - Performance tracking data
4. **kitchen_load_patterns** - Hourly load patterns for optimization

### Environment Variables (.env)
```env
# Core Configuration
EXCEL_FILE_PATH=data/kitchen_config.xlsx
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
API_HOST=0.0.0.0
API_PORT=8000

# System Tuning
MAX_STARVATION_COUNT=3
SYNCHRONIZATION_WINDOW_MINUTES=3
PERFORMANCE_HISTORY_DAYS=30
DEBUG_MODE=True
LOG_LEVEL=INFO
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --api          # API tests only
python run_tests.py --performance  # Performance tests only

# Run with coverage
python run_tests.py --coverage

# Quick tests (skip slow tests)
python run_tests.py --fast
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component interaction testing
- **API Tests**: Complete API endpoint testing
- **Performance Tests**: Load and scalability testing

## 📚 Documentation

- **[Docker Deployment Guide](DOCKER_DEPLOYMENT.md)** - Complete Docker setup and deployment
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Manual setup instructions
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Detailed API reference
- **[User Guide](docs/USER_GUIDE.md)** - User manual and best practices

## 🚀 Deployment Options

### Docker (Recommended)
```bash
# Quick start
./scripts/start-system.sh  # Linux/Mac
scripts\start-system.bat   # Windows

# Manual Docker Compose
docker-compose up -d

# Test deployment
./scripts/test-deployment.sh
```

### Development
```bash
# Backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Production
```bash
# With custom configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production
```bash
./deploy.sh production
```

## 🔍 Monitoring & Health

### Health Checks
- Application: `GET /api/system/health`
- Individual components status
- Resource utilization monitoring
- Performance metrics tracking

### Logging
- Structured logging with configurable levels
- Request/response logging
- Error tracking and alerting
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- Check the [Installation Guide](docs/INSTALLATION_GUIDE.md) for setup issues
- Review [API Documentation](docs/API_DOCUMENTATION.md) for usage
- Run health checks: `curl http://localhost:8000/api/system/health`
- Check application logs in `logs/kitchen_queue.log`

---

**Smart Kitchen Queue Management System** - Optimizing kitchen operations with AI-driven intelligence.
