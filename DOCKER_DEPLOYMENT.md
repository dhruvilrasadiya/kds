# Smart Kitchen Queue Management System - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Smart Kitchen Queue Management System using Docker and Docker Compose.

## 🏗️ Architecture Overview

The system consists of 4 main services:

- **Frontend** (React + Vite) - Port 8080
- **Backend** (FastAPI + Python) - Port 8000  
- **MongoDB** (Database) - Port 27017
- **Ollama** (AI/LLM Service) - Port 11434

All services are connected via a custom Docker network with proper health checks and dependency management.

## 📋 Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0 or higher
- **Git** (to clone the repository)
- **curl** (for health checks)

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended for Ollama)
- **Storage**: 10GB free space (for Docker images and Ollama models)
- **CPU**: Multi-core processor recommended

### Verify Installation
```bash
docker --version
docker-compose --version
# or
docker compose version
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Windows:**
```cmd
scripts\start-system.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/start-system.sh
```

### Option 2: Manual Startup

1. **Start Infrastructure Services:**
```bash
docker-compose up -d mongodb ollama
```

2. **Wait for Services to be Ready:**
```bash
# Check MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Check Ollama
curl http://localhost:11434/api/tags
```

3. **Start Application Services:**
```bash
docker-compose up -d backend frontend
```

4. **Verify All Services:**
```bash
docker-compose ps
```

## 🔧 Configuration

### Environment Variables

The system uses environment variables for configuration. Key variables include:

**Database:**
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DATABASE`: Database name (default: smart_kitchen)

**AI Service:**
- `OLLAMA_BASE_URL`: Ollama service URL
- `OLLAMA_MODEL`: AI model to use (default: llama3.1:8b)

**API:**
- `API_HOST`: Backend host (default: 0.0.0.0)
- `API_PORT`: Backend port (default: 8000)
- `DEBUG_MODE`: Enable debug mode (default: false)

### Custom Configuration

To override default settings, create a `.env` file in the project root:

```env
# Custom MongoDB credentials
MONGODB_URL=mongodb://admin:your_password@mongodb:27017/smart_kitchen?authSource=admin

# Custom Ollama model
OLLAMA_MODEL=llama3.1:8b

# Enable debug mode
DEBUG_MODE=true
```

## 📊 Service Details

### Frontend Service
- **Technology**: React 18 + Vite + TypeScript
- **Port**: 8080
- **Build**: Multi-stage Docker build with Nginx
- **Features**: 
  - Production-optimized build
  - Gzip compression
  - Client-side routing support
  - API proxy configuration

### Backend Service
- **Technology**: FastAPI + Python 3.11
- **Port**: 8000
- **Features**:
  - Async/await support
  - MongoDB integration
  - Ollama AI integration
  - Excel data management
  - Real-time queue management

### MongoDB Service
- **Version**: MongoDB 7.0
- **Port**: 27017
- **Features**:
  - Automatic database initialization
  - Collection validation schemas
  - Optimized indexes
  - Persistent data storage

### Ollama Service
- **Technology**: Ollama AI platform
- **Port**: 11434
- **Model**: llama3.1:8b (auto-downloaded)
- **Features**:
  - Local AI inference
  - Model management
  - API-based interaction

## 🔍 Monitoring & Logs

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
docker-compose logs -f ollama
```

### Health Checks
All services include health checks accessible via:
- Frontend: http://localhost:8080/health
- Backend: http://localhost:8000/health
- MongoDB: Built-in ping command
- Ollama: http://localhost:11434/api/tags

## 🛠️ Management Commands

### Start System
```bash
# Automated (recommended)
./scripts/start-system.sh

# Manual
docker-compose up -d
```

### Stop System
```bash
# Graceful shutdown
./scripts/stop-system.sh

# Manual
docker-compose down
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Update Services
```bash
# Rebuild and restart
docker-compose up -d --build

# Force rebuild
docker-compose build --no-cache
docker-compose up -d
```

## 🗄️ Data Management

### Persistent Data
Data is stored in Docker volumes:
- `mongodb_data`: Database files
- `ollama_data`: AI models and cache

### Backup Data
```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out /data/backup

# Copy backup to host
docker cp kds-mongodb:/data/backup ./mongodb-backup
```

### Restore Data
```bash
# Copy backup to container
docker cp ./mongodb-backup kds-mongodb:/data/restore

# Restore MongoDB
docker-compose exec mongodb mongorestore /data/restore
```

## 🔒 Security Considerations

### Production Deployment
1. **Change Default Passwords**: Update MongoDB credentials
2. **Use HTTPS**: Configure SSL/TLS certificates
3. **Network Security**: Restrict port access
4. **Environment Variables**: Use Docker secrets for sensitive data
5. **Regular Updates**: Keep Docker images updated

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 8080  # Frontend
ufw allow 8000  # Backend (if external access needed)
# Keep 27017 and 11434 internal only
```

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
netstat -tulpn | grep :8080

# Stop conflicting services
sudo systemctl stop apache2  # Example
```

**2. MongoDB Connection Failed**
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

**3. Ollama Model Download Failed**
```bash
# Manual model download
docker-compose exec ollama ollama pull llama3.1:8b

# Check available models
docker-compose exec ollama ollama list
```

**4. Frontend Build Failed**
```bash
# Check build logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
```

### Performance Optimization

**1. Increase Memory for Ollama**
```yaml
# In docker-compose.yml
ollama:
  deploy:
    resources:
      limits:
        memory: 8G
```

**2. MongoDB Performance**
```yaml
# In docker-compose.yml
mongodb:
  command: mongod --wiredTigerCacheSizeGB 2
```

## 📱 Access Points

Once deployed, access the system via:

- **Main Application**: http://localhost:8080
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **MongoDB**: mongodb://localhost:27017 (admin/password123)
- **Ollama API**: http://localhost:11434/api/tags

## 🔄 Updates & Maintenance

### Regular Maintenance
```bash
# Update images
docker-compose pull

# Clean up unused resources
docker system prune -f

# Update and restart
docker-compose up -d --build
```

### Version Updates
1. Pull latest code: `git pull origin main`
2. Rebuild images: `docker-compose build --no-cache`
3. Restart services: `docker-compose up -d`

---

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify service health: `docker-compose ps`
3. Review this documentation
4. Check the main README.md for additional information

**Happy cooking! 🍳**
