# SMART FLOW v2 Deployment Guide

## Overview

This guide covers deploying SMART FLOW v2 in various environments, from development to production. It includes installation steps, configuration, optimization, monitoring, and troubleshooting.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Development Deployment](#development-deployment)
4. [Production Deployment](#production-deployment)
5. [Multi-Intersection Setup](#multi-intersection-setup)
6. [Dashboard Deployment](#dashboard-deployment)
7. [Performance Tuning](#performance-tuning)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Security](#security)
10. [Backup and Recovery](#backup-and-recovery)
11. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

**Hardware:**
- CPU: Dual-core 2.0 GHz or higher
- RAM: 4GB
- Storage: 5GB free space
- Network: 10 Mbps (for live streams)

**Software:**
- Operating System: Ubuntu 20.04+, Windows 10+, macOS 10.15+
- Python: 3.8 or higher
- Node.js: 16+ (for dashboard frontend)

### Recommended Requirements

**Hardware:**
- CPU: Quad-core 3.0 GHz or higher
- RAM: 8GB or more
- GPU: NVIDIA GPU with CUDA support (GTX 1060 or better)
- Storage: 20GB free space (SSD recommended)
- Network: 50 Mbps or higher

**Software:**
- Operating System: Ubuntu 22.04 LTS
- Python: 3.9 or 3.10
- CUDA: 11.8 or 12.1 (for GPU acceleration)
- Node.js: 18 LTS

### Production Requirements

**Hardware:**
- CPU: 8-core 3.5 GHz or higher
- RAM: 16GB or more
- GPU: NVIDIA RTX 3060 or better
- Storage: 100GB SSD
- Network: 100 Mbps dedicated connection
- UPS: Uninterruptible power supply recommended

**Software:**
- Operating System: Ubuntu 22.04 LTS Server
- Python: 3.10
- CUDA: 12.1
- Docker: 24.0+ (optional)
- Nginx: 1.18+ (for reverse proxy)

---

## Installation

### 1. System Preparation

#### Ubuntu/Debian

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.10 python3.10-venv python3-pip \
    build-essential cmake git wget curl \
    libopencv-dev python3-opencv \
    ffmpeg libavcodec-dev libavformat-dev libswscale-dev

# Install NVIDIA drivers (if using GPU)
sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit

# Verify GPU
nvidia-smi
```

#### Windows

```powershell
# Install Python 3.10 from python.org
# Install Visual Studio Build Tools
# Install CUDA Toolkit from NVIDIA website
# Install FFmpeg from ffmpeg.org

# Verify installations
python --version
nvcc --version
ffmpeg -version
```

#### macOS

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 ffmpeg opencv

# Verify installations
python3 --version
ffmpeg -version
```

### 2. Clone Repository

```bash
# Clone repository
git clone https://github.com/yourusername/smart-flow-v2.git
cd smart-flow-v2

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# For GPU support (CUDA 11.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify installation
python -c "import cv2, ultralytics, fastapi; print('Dependencies OK')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 4. Download YOLO Model

```bash
# Download YOLOv8 nano model (automatic on first run)
# Or download manually:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# For better accuracy, download larger models:
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt
```

### 5. Install Dashboard Frontend (Optional)

```bash
# Install Node.js and npm
# Ubuntu:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version
npm --version

# Install frontend dependencies
cd dashboard/frontend
npm install
cd ../..
```

---

## Development Deployment

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run with sample video
python main.py --source data/testvid.mp4

# Run with dashboard
python main.py --source data/testvid.mp4 --dashboard --port 8080
```

### Development Configuration

Create `config/dev_config.json`:

```json
{
  "intersection": {
    "name": "Development Test",
    "video_source": "data/testvid.mp4"
  },
  "lanes": {
    "north": {
      "region": [100, 0, 300, 400],
      "direction": "north",
      "minimum_green": 10,
      "maximum_green": 60
    }
  },
  "signal_timing": {
    "yellow_duration": 3,
    "all_red_duration": 2,
    "cycle_interval_frames": 30
  },
  "detection": {
    "model_path": "yolov8n.pt",
    "confidence_threshold": 0.5
  },
  "features": {
    "pedestrian_management": true,
    "emergency_priority": true,
    "turn_lane_control": false,
    "queue_estimation": true
  },
  "dashboard": {
    "enabled": true,
    "port": 8080,
    "websocket_update_interval": 0.5
  }
}
```

Run with configuration:

```bash
python main.py --config config/dev_config.json
```

### Development Dashboard

```bash
# Terminal 1: Run backend
python main.py --source data/testvid.mp4 --dashboard --port 8080

# Terminal 2: Run frontend (development mode)
cd dashboard/frontend
npm start

# Access at:
# Backend API: http://localhost:8080
# Frontend: http://localhost:3000
```

---

## Production Deployment

### 1. Production Configuration

Create `config/production_config.json`:

```json
{
  "intersection": {
    "name": "Main & 5th Production",
    "video_source": "rtsp://username:password@camera.ip:554/stream",
    "video_source_type": "rtsp"
  },
  "lanes": {
    // Production lane configuration
  },
  "signal_timing": {
    "yellow_duration": 4,
    "all_red_duration": 2,
    "cycle_interval_frames": 30
  },
  "detection": {
    "model_path": "yolov8m.pt",
    "confidence_threshold": 0.6,
    "enable_tracking": true
  },
  "features": {
    "pedestrian_management": true,
    "emergency_priority": true,
    "turn_lane_control": true,
    "queue_estimation": true,
    "object_tracking": true
  },
  "dashboard": {
    "enabled": true,
    "port": 8080,
    "host": "0.0.0.0",
    "websocket_update_interval": 1.0,
    "enable_manual_override": true
  }
}
```

### 2. Systemd Service (Linux)

Create `/etc/systemd/system/smartflow.service`:

```ini
[Unit]
Description=SMART FLOW v2 Traffic Management System
After=network.target

[Service]
Type=simple
User=smartflow
Group=smartflow
WorkingDirectory=/opt/smartflow
Environment="PATH=/opt/smartflow/venv/bin"
ExecStart=/opt/smartflow/venv/bin/python main.py \
    --config /opt/smartflow/config/production_config.json \
    --dashboard \
    --no-display \
    --log-level INFO
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
# Create user
sudo useradd -r -s /bin/false smartflow

# Set permissions
sudo chown -R smartflow:smartflow /opt/smartflow

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable smartflow
sudo systemctl start smartflow

# Check status
sudo systemctl status smartflow

# View logs
sudo journalctl -u smartflow -f
```

### 3. Nginx Reverse Proxy

Install and configure Nginx:

```bash
# Install Nginx
sudo apt install -y nginx

# Create configuration
sudo nano /etc/nginx/sites-available/smartflow
```

Nginx configuration:

```nginx
upstream smartflow_backend {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name traffic.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name traffic.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/traffic.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/traffic.yourdomain.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # API endpoints
    location /api/ {
        proxy_pass http://smartflow_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://smartflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Video stream
    location /stream {
        proxy_pass http://smartflow_backend;
        proxy_buffering off;
        proxy_set_header Host $host;
    }

    # Frontend (if serving static files)
    location / {
        root /opt/smartflow/dashboard/frontend/build;
        try_files $uri /index.html;
    }

    # Logging
    access_log /var/log/nginx/smartflow_access.log;
    error_log /var/log/nginx/smartflow_error.log;
}
```

Enable configuration:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smartflow /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d traffic.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### 5. Build Frontend for Production

```bash
cd dashboard/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Copy build to deployment location
sudo cp -r build /opt/smartflow/dashboard/frontend/
```

---

## Multi-Intersection Setup

### 1. Network Configuration

Create `config/network_production.yaml`:

```yaml
network:
  name: "Downtown Corridor Production"
  coordination_enabled: true
  target_speed_mph: 35
  update_interval_seconds: 1.0

intersections:
  intersection_1:
    name: "Main & 1st"
    video_source: "rtsp://camera1.ip/stream"
    config_file: "config/intersection_1.json"
  
  intersection_2:
    name: "Main & 2nd"
    video_source: "rtsp://camera2.ip/stream"
    config_file: "config/intersection_2.json"
  
  intersection_3:
    name: "Main & 3rd"
    video_source: "rtsp://camera3.ip/stream"
    config_file: "config/intersection_3.json"

connections:
  - from: "intersection_1"
    to: "intersection_2"
    travel_time_seconds: 30
    distance_meters: 400
  
  - from: "intersection_2"
    to: "intersection_3"
    travel_time_seconds: 25
    distance_meters: 350
```

### 2. Distributed Deployment

For large networks, deploy each intersection on separate servers:

**Server 1 (Intersection 1):**
```bash
python main.py --config config/intersection_1.json \
    --dashboard --port 8081 \
    --coordinator-mode client \
    --coordinator-host coordinator.local
```

**Server 2 (Intersection 2):**
```bash
python main.py --config config/intersection_2.json \
    --dashboard --port 8082 \
    --coordinator-mode client \
    --coordinator-host coordinator.local
```

**Coordinator Server:**
```bash
python coordinator.py --config config/network_production.yaml \
    --dashboard --port 8080
```

### 3. Network Monitoring

Monitor network coordination:

```bash
# Check coordination status
curl http://coordinator.local:8080/api/intersections

# View network metrics
curl http://coordinator.local:8080/api/metrics

# Monitor logs
sudo journalctl -u smartflow-coordinator -f
```

---

## Dashboard Deployment

### Frontend Build and Deployment

```bash
# Build frontend
cd dashboard/frontend
npm run build

# Deploy to web server
sudo cp -r build/* /var/www/smartflow/

# Or serve with Nginx (see Nginx configuration above)
```

### Dashboard Security

#### 1. Enable Authentication

Add authentication middleware (example with JWT):

```python
# In src/web_dashboard.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    token = credentials.credentials
    # Verify token
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.get("/api/metrics", dependencies=[Depends(verify_token)])
async def get_metrics():
    # Protected endpoint
    pass
```

#### 2. Configure CORS

For production, restrict CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://traffic.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

#### 3. Rate Limiting

Implement rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/metrics")
@limiter.limit("100/minute")
async def get_metrics(request: Request):
    # Rate-limited endpoint
    pass
```

---

## Performance Tuning

### 1. GPU Optimization

```bash
# Verify GPU usage
nvidia-smi -l 1

# Set GPU memory growth
export TF_FORCE_GPU_ALLOW_GROWTH=true

# Use specific GPU
export CUDA_VISIBLE_DEVICES=0
```

### 2. Model Selection

Choose appropriate YOLO model:

```bash
# Fast (30+ FPS): yolov8n.pt
python main.py --model yolov8n.pt

# Balanced (20-25 FPS): yolov8s.pt
python main.py --model yolov8s.pt

# Accurate (15-20 FPS): yolov8m.pt
python main.py --model yolov8m.pt

# Most accurate (10-15 FPS): yolov8l.pt
python main.py --model yolov8l.pt
```

### 3. Video Processing Optimization

```bash
# Reduce cycle interval for faster updates
python main.py --cycle-interval 15

# Disable visualization for headless operation
python main.py --no-display

# Reduce dashboard update frequency
# In config: "websocket_update_interval": 2.0
```

### 4. System Optimization

```bash
# Increase file descriptor limit
ulimit -n 65536

# Optimize network settings
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# Disable CPU frequency scaling
sudo cpupower frequency-set -g performance
```

### 5. Database Optimization (if using)

```bash
# Use PostgreSQL for metrics storage
# Configure connection pooling
# Index frequently queried fields
# Implement data retention policies
```

---

## Monitoring and Logging

### 1. Application Logging

Configure logging in `config/logging.conf`:

```ini
[loggers]
keys=root,smartflow

[handlers]
keys=console,file,syslog

[formatters]
keys=detailed

[logger_root]
level=INFO
handlers=console,file

[logger_smartflow]
level=DEBUG
handlers=file,syslog
qualname=smartflow
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=detailed
args=(sys.stdout,)

[handler_file]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=detailed
args=('/var/log/smartflow/smartflow.log', 'a', 10485760, 5)

[handler_syslog]
class=handlers.SysLogHandler
level=WARNING
formatter=detailed
args=('/dev/log',)

[formatter_detailed]
format=%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s
```

### 2. System Monitoring

Install monitoring tools:

```bash
# Install Prometheus and Grafana
sudo apt install -y prometheus grafana

# Configure Prometheus to scrape metrics
# Add to /etc/prometheus/prometheus.yml:
```

```yaml
scrape_configs:
  - job_name: 'smartflow'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### 3. Health Checks

Implement health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": get_uptime(),
        "video_source": "connected",
        "detection": "active"
    }
```

Monitor with:

```bash
# Simple check
curl http://localhost:8080/health

# Continuous monitoring
watch -n 5 curl -s http://localhost:8080/health
```

### 4. Log Rotation

Configure logrotate:

```bash
# Create /etc/logrotate.d/smartflow
sudo nano /etc/logrotate.d/smartflow
```

```
/var/log/smartflow/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 smartflow smartflow
    sharedscripts
    postrotate
        systemctl reload smartflow > /dev/null 2>&1 || true
    endscript
}
```

---

## Security

### 1. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Restrict dashboard access to specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 8080
```

### 2. Secure Video Streams

```bash
# Use RTSP over TLS (RTSPS)
# Configure camera for RTSPS
# Use strong credentials

# Example RTSPS URL:
rtsps://username:strong_password@camera.ip:322/stream
```

### 3. Environment Variables

Store sensitive data in environment variables:

```bash
# Create .env file
cat > .env << EOF
VIDEO_SOURCE=rtsp://username:password@camera.ip/stream
DASHBOARD_SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:pass@localhost/smartflow
WEATHER_API_KEY=your_api_key
EOF

# Secure .env file
chmod 600 .env

# Load in application
from dotenv import load_dotenv
load_dotenv()
```

### 4. Regular Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt

# Update YOLO models
# Download latest models periodically
```

---

## Backup and Recovery

### 1. Configuration Backup

```bash
# Backup configuration
tar -czf smartflow-config-$(date +%Y%m%d).tar.gz config/

# Backup to remote server
rsync -avz config/ backup-server:/backups/smartflow/config/
```

### 2. Database Backup

```bash
# PostgreSQL backup
pg_dump smartflow > smartflow-$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/smartflow"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump smartflow | gzip > $BACKUP_DIR/smartflow-$DATE.sql.gz
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 3. Disaster Recovery

```bash
# Stop service
sudo systemctl stop smartflow

# Restore configuration
tar -xzf smartflow-config-20240115.tar.gz -C /opt/smartflow/

# Restore database
psql smartflow < smartflow-20240115.sql

# Start service
sudo systemctl start smartflow
```

---

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

```bash
# Check service status
sudo systemctl status smartflow

# View logs
sudo journalctl -u smartflow -n 100

# Check configuration
python main.py --config config/production_config.json --validate

# Test manually
sudo -u smartflow /opt/smartflow/venv/bin/python main.py --config config/production_config.json
```

#### 2. High CPU Usage

```bash
# Check process
top -p $(pgrep -f smartflow)

# Reduce processing load
# - Use smaller YOLO model
# - Increase cycle interval
# - Disable heavy features
```

#### 3. Memory Leaks

```bash
# Monitor memory
watch -n 1 'ps aux | grep smartflow'

# Restart service periodically (temporary fix)
# Add to crontab:
0 3 * * * systemctl restart smartflow
```

#### 4. Video Stream Issues

```bash
# Test stream with VLC
vlc rtsp://camera.ip/stream

# Check network connectivity
ping camera.ip

# Verify credentials
curl -u username:password rtsp://camera.ip/stream
```

#### 5. Dashboard Not Accessible

```bash
# Check if service is running
sudo systemctl status smartflow

# Check port
sudo netstat -tlnp | grep 8080

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

### Performance Issues

```bash
# Profile application
python -m cProfile -o profile.stats main.py --config config/production_config.json

# Analyze profile
python -m pstats profile.stats

# Monitor GPU
nvidia-smi -l 1

# Monitor network
iftop -i eth0
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check service status
- Review error logs
- Monitor disk space

**Weekly:**
- Review performance metrics
- Check for updates
- Verify backups

**Monthly:**
- Update dependencies
- Review and optimize configuration
- Test disaster recovery procedures
- Clean old logs and data

### Maintenance Scripts

```bash
# Daily health check
#!/bin/bash
if ! systemctl is-active --quiet smartflow; then
    echo "SMART FLOW service is down!" | mail -s "Alert" admin@example.com
    systemctl restart smartflow
fi

# Weekly cleanup
#!/bin/bash
find /var/log/smartflow -name "*.log" -mtime +30 -delete
find /opt/smartflow/output -name "*.mp4" -mtime +7 -delete
```

---

## Support

For deployment issues:
- Review this guide
- Check system logs
- Consult troubleshooting section
- Open an issue on GitHub

---

## License

MIT License - See LICENSE file for details
