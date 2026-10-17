# Smart Kitchen Queue Management System - Deployment Guide

## Deployment Options

### 1. Local Development Deployment

#### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd kds

# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Download AI model
ollama pull llama2

# Start application
python main.py
```

### 2. Docker Deployment (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Deployment Steps
```bash
# Clone repository
git clone <repository-url>
cd kds

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f kitchen-app
```

#### Service Configuration
The Docker deployment includes:
- **kitchen-app**: Main application (port 8000)
- **ollama**: AI service (port 11434)
- **redis**: Caching (port 6379)
- **nginx**: Reverse proxy (ports 80/443)

### 3. Production Deployment

#### System Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 50GB+ SSD
- **Network**: Stable internet connection

#### Security Considerations

##### 1. Environment Variables
```bash
# Production .env
DEBUG_MODE=False
LOG_LEVEL=WARNING
API_HOST=127.0.0.1  # Bind to localhost only
```

##### 2. Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 8000/tcp  # Block direct access to app
ufw deny 11434/tcp # Block direct access to Ollama
```

##### 3. SSL/TLS Setup
```bash
# Generate SSL certificates (example with Let's Encrypt)
certbot --nginx -d your-domain.com

# Or use self-signed certificates for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

##### 4. Database Security
- Use strong passwords
- Enable encryption at rest
- Regular backups
- Network isolation

#### Performance Optimization

##### 1. Application Tuning
```python
# In production, consider these settings:
PERFORMANCE_HISTORY_DAYS=7  # Reduce memory usage
MAX_STARVATION_COUNT=2      # Faster response
SYNCHRONIZATION_WINDOW_MINUTES=2
```

##### 2. AI Model Optimization
```bash
# Use optimized models for production
ollama pull mistral:7b-instruct  # Faster inference
# or
ollama pull codellama:7b         # Code-optimized
```

##### 3. Caching Strategy
```python
# Enable Redis caching
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300  # 5 minutes
```

### 4. Cloud Deployment

#### AWS Deployment

##### Using ECS (Elastic Container Service)
```yaml
# ecs-task-definition.json
{
  "family": "kitchen-queue-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "kitchen-app",
      "image": "your-registry/kitchen-queue-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OLLAMA_BASE_URL",
          "value": "http://ollama-service:11434"
        }
      ]
    }
  ]
}
```

##### Using EC2
```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-903004f8

# Deploy using Docker
scp -i your-key.pem docker-compose.yml ec2-user@your-instance:/home/ec2-user/
ssh -i your-key.pem ec2-user@your-instance
docker-compose up -d
```

#### Google Cloud Platform

##### Using Cloud Run
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/kitchen-queue-system', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/kitchen-queue-system']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'kitchen-queue-system',
         '--image', 'gcr.io/$PROJECT_ID/kitchen-queue-system',
         '--platform', 'managed',
         '--region', 'us-central1']
```

#### Azure Deployment

##### Using Container Instances
```bash
az container create \
  --resource-group myResourceGroup \
  --name kitchen-queue-system \
  --image your-registry/kitchen-queue-system:latest \
  --ports 8000 \
  --environment-variables OLLAMA_BASE_URL=http://ollama:11434
```

### 5. Kubernetes Deployment

#### Deployment Manifests
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kitchen-queue-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kitchen-queue-system
  template:
    metadata:
      labels:
        app: kitchen-queue-system
    spec:
      containers:
      - name: kitchen-app
        image: kitchen-queue-system:latest
        ports:
        - containerPort: 8000
        env:
        - name: OLLAMA_BASE_URL
          value: "http://ollama-service:11434"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: kitchen-queue-service
spec:
  selector:
    app: kitchen-queue-system
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Deploy to Kubernetes
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

### 6. Monitoring and Logging

#### Application Monitoring
```python
# Add to requirements.txt
prometheus-client==0.17.1
```

```python
# In main.py
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
order_counter = Counter('orders_total', 'Total orders processed')
response_time = Histogram('response_time_seconds', 'Response time')
```

#### Log Aggregation
```yaml
# docker-compose.yml addition
  fluentd:
    image: fluent/fluentd:v1.14-1
    volumes:
      - ./fluentd.conf:/fluentd/etc/fluent.conf
      - ./logs:/var/log/kitchen
```

#### Health Checks
```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /api/system/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

### 7. Backup and Recovery

#### Data Backup
```bash
# Backup Excel configuration
cp data/kitchen_config.xlsx backups/kitchen_config_$(date +%Y%m%d).xlsx

# Backup logs
tar -czf backups/logs_$(date +%Y%m%d).tar.gz logs/
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
cp data/kitchen_config.xlsx $BACKUP_DIR/config_$DATE.xlsx

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.xlsx" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 8. Scaling Considerations

#### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Implement session affinity if needed
- Scale AI service separately

#### Vertical Scaling
- Monitor CPU/memory usage
- Adjust container resources
- Optimize AI model size

#### Database Scaling
- Consider PostgreSQL for production
- Implement read replicas
- Use connection pooling

### 9. Troubleshooting

#### Common Issues
1. **High Memory Usage**: Reduce AI model size or history retention
2. **Slow Response**: Check AI service performance, add caching
3. **Connection Errors**: Verify network configuration and firewall rules

#### Debugging Commands
```bash
# Check container logs
docker-compose logs -f kitchen-app

# Check system resources
docker stats

# Test API endpoints
curl -f http://localhost:8000/api/system/health

# Monitor AI service
curl http://localhost:11434/api/version
```

### 10. Maintenance

#### Regular Tasks
- Update dependencies monthly
- Review and rotate logs weekly
- Monitor system performance daily
- Backup configuration files daily

#### Update Procedure
```bash
# 1. Backup current system
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Test in staging
python -m pytest tests/

# 5. Deploy to production
docker-compose up -d --build
```

This deployment guide provides comprehensive instructions for various deployment scenarios, from development to production-ready systems.
