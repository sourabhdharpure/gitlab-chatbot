# GitLab AI Assistant - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 2GB
- **Storage**: 10GB
- **OS**: Linux, macOS, or Windows
- **Python**: 3.8 or higher

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 4GB+
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Python**: 3.11+

### Software Dependencies

- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-container setup)
- **Git**: 2.30+ (for version control)
- **curl**: For health checks and testing

### API Requirements

- **Google Gemini API Key**: Required for AI functionality
- **Internet Connection**: For API calls and model downloads

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/gitlab-chatbot.git
cd gitlab-chatbot
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp env_example.txt .env

# Edit environment variables
nano .env
```

**Required Environment Variables**:
```bash
# Google Gemini API Key (Required)
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Custom configuration
STREAMLIT_SERVER_PORT=8507
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

### 5. Initialize Data

```bash
# Create data directories
mkdir -p data/chroma_db data/logs

# Initialize vector database (if not already done)
python -c "
from src.vector_store import build_vector_store_from_data
build_vector_store_from_data('data/chunks.json')
"
```

### 6. Run Application

```bash
# Development mode
streamlit run app.py --server.port 8507

# Production mode with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8507 app:main
```

### 7. Verify Installation

```bash
# Health check
curl http://localhost:8507/health

# Test chat endpoint
curl -X POST http://localhost:8507/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is GitLab?"}'
```

## Docker Deployment

### 1. Build Docker Image

```bash
# Build image
docker build -t gitlab-chatbot:latest .

# Verify image
docker images gitlab-chatbot
```

### 2. Run Container

```bash
# Run with environment variables
docker run -d \
  --name gitlab-chatbot \
  -p 8507:8507 \
  -e GOOGLE_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  gitlab-chatbot:latest

# Check container status
docker ps
docker logs gitlab-chatbot
```

### 3. Docker Compose

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f gitlab-chatbot
```

## Production Deployment

### 1. Server Preparation

#### Ubuntu/Debian Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### CentOS/RHEL Setup

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Application Deployment

#### Create Production Directory

```bash
# Create application directory
sudo mkdir -p /opt/gitlab-chatbot
cd /opt/gitlab-chatbot

# Clone repository
sudo git clone https://github.com/your-org/gitlab-chatbot.git .

# Set permissions
sudo chown -R $USER:$USER /opt/gitlab-chatbot
```

#### Configure Environment

```bash
# Create production environment file
cat > .env << EOF
GOOGLE_API_KEY=your_production_api_key
STREAMLIT_SERVER_PORT=8507
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

# Secure environment file
chmod 600 .env
```

#### Deploy with Docker Compose

```bash
# Deploy production stack
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### 3. Nginx Configuration

#### Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/gitlab-chatbot
```

**Nginx Configuration**:
```nginx
upstream gitlab_chatbot {
    server 127.0.0.1:8507;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://gitlab_chatbot;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://gitlab_chatbot/health;
        access_log off;
    }
}
```

#### Enable Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gitlab-chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 4. SSL Certificate

```bash
# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 5. System Service

#### Create Systemd Service

```bash
sudo nano /etc/systemd/system/gitlab-chatbot.service
```

**Service Configuration**:
```ini
[Unit]
Description=GitLab AI Assistant
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/gitlab-chatbot
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

#### Enable Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable gitlab-chatbot

# Start service
sudo systemctl start gitlab-chatbot

# Check status
sudo systemctl status gitlab-chatbot
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance

```bash
# Launch EC2 instance (t3.medium or larger)
# Install Docker and dependencies
# Follow production deployment steps

# Configure security groups
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 22 (SSH)
```

#### ECS Deployment

```yaml
# task-definition.json
{
  "family": "gitlab-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "gitlab-chatbot",
      "image": "your-account.dkr.ecr.region.amazonaws.com/gitlab-chatbot:latest",
      "portMappings": [
        {
          "containerPort": 8507,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GOOGLE_API_KEY",
          "value": "your-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gitlab-chatbot",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/gitlab-chatbot

# Deploy to Cloud Run
gcloud run deploy gitlab-chatbot \
  --image gcr.io/PROJECT-ID/gitlab-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your-api-key
```

### Azure Deployment

#### Container Instances

```bash
# Create resource group
az group create --name gitlab-chatbot-rg --location eastus

# Deploy container
az container create \
  --resource-group gitlab-chatbot-rg \
  --name gitlab-chatbot \
  --image your-registry/gitlab-chatbot:latest \
  --dns-name-label gitlab-chatbot \
  --ports 8507 \
  --environment-variables GOOGLE_API_KEY=your-api-key
```

## Monitoring and Maintenance

### 1. Health Monitoring

#### Application Health

```bash
# Health check script
#!/bin/bash
HEALTH_URL="http://localhost:8507/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Application is healthy"
    exit 0
else
    echo "Application is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

#### System Monitoring

```bash
# Monitor system resources
htop
iostat -x 1
df -h
free -h
```

### 2. Log Management

#### Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/gitlab-chatbot
```

**Logrotate Configuration**:
```
/opt/gitlab-chatbot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/gitlab-chatbot/docker-compose.prod.yml restart gitlab-chatbot
    endscript
}
```

#### Log Analysis

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f gitlab-chatbot

# Analyze error logs
grep "ERROR" /opt/gitlab-chatbot/logs/app.log | tail -20

# Monitor performance
grep "response_time" /opt/gitlab-chatbot/logs/app.log | awk '{print $NF}' | sort -n
```

### 3. Backup Strategy

#### Data Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/gitlab-chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data directory
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/gitlab-chatbot/data/

# Backup configuration
cp /opt/gitlab-chatbot/.env $BACKUP_DIR/env_$DATE

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/data_$DATE.tar.gz"
```

#### Automated Backup

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/gitlab-chatbot/backup.sh
```

### 4. Updates and Maintenance

#### Application Updates

```bash
# Update application
cd /opt/gitlab-chatbot
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Verify update
curl http://localhost:8507/health
```

#### Database Maintenance

```bash
# Optimize vector database
docker exec gitlab-chatbot python -c "
from src.vector_store import VectorStore
vs = VectorStore('data/chroma_db')
vs.optimize()
"

# Clean up old cache files
find /opt/gitlab-chatbot/data -name "*.json" -mtime +30 -delete
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms**: Container fails to start or exits immediately

**Diagnosis**:
```bash
# Check container logs
docker logs gitlab-chatbot

# Check system resources
free -h
df -h
```

**Solutions**:
- Verify API key is set correctly
- Check available memory and disk space
- Ensure ports are not in use
- Verify Docker is running

#### 2. High Memory Usage

**Symptoms**: Application consumes excessive memory

**Diagnosis**:
```bash
# Monitor memory usage
docker stats gitlab-chatbot

# Check for memory leaks
docker exec gitlab-chatbot ps aux --sort=-%mem
```

**Solutions**:
- Increase container memory limits
- Optimize vector database
- Clear cache periodically
- Restart application

#### 3. Slow Response Times

**Symptoms**: Chat responses are slow

**Diagnosis**:
```bash
# Check performance metrics
curl http://localhost:8507/api/metrics

# Monitor system resources
htop
iostat -x 1
```

**Solutions**:
- Check cache hit rates
- Optimize vector search
- Scale horizontally
- Check network latency

#### 4. API Errors

**Symptoms**: API calls return errors

**Diagnosis**:
```bash
# Check API logs
grep "ERROR" /opt/gitlab-chatbot/logs/app.log

# Test API endpoints
curl -v http://localhost:8507/health
```

**Solutions**:
- Verify API key validity
- Check rate limits
- Review error logs
- Restart application

### Performance Optimization

#### 1. Cache Optimization

```bash
# Monitor cache performance
curl http://localhost:8507/api/cache/stats

# Clear cache if needed
curl -X POST http://localhost:8507/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"cache_type": "all", "confirm": true}'
```

#### 2. Database Optimization

```bash
# Optimize vector database
docker exec gitlab-chatbot python -c "
from src.vector_store import VectorStore
vs = VectorStore('data/chroma_db')
vs.optimize()
print('Database optimized')
"
```

#### 3. System Optimization

```bash
# Optimize system settings
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'net.core.somaxconn=65535' >> /etc/sysctl.conf
sysctl -p
```

### Emergency Procedures

#### 1. Service Recovery

```bash
# Restart all services
sudo systemctl restart gitlab-chatbot

# If systemd service fails, restart manually
cd /opt/gitlab-chatbot
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

#### 2. Data Recovery

```bash
# Restore from backup
cd /opt/gitlab-chatbot
docker-compose -f docker-compose.prod.yml down
tar -xzf /opt/backups/gitlab-chatbot/data_YYYYMMDD_HHMMSS.tar.gz
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Complete Rebuild

```bash
# Complete system rebuild
cd /opt/gitlab-chatbot
docker-compose -f docker-compose.prod.yml down
docker system prune -a
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

This deployment guide provides comprehensive instructions for deploying the GitLab AI Assistant in various environments. For additional support, please refer to the technical documentation or contact the development team.
