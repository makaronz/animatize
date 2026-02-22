> [!WARNING]
> **DEPRECATED / OUTDATED**: This document may contain historical flows and commands that are not the canonical runtime path anymore.
> Use **README.md** for onboarding and runtime startup, **docs/API.md** for endpoints, **docs/ARCHITECTURE.md** for system flow, and **docs/OPERATIONS.md** for troubleshooting.

# 🚀 ANIMAtiZE Framework - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Manual Deployment](#manual-deployment)
- [PyPI Installation](#pypi-installation)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers all deployment options for the ANIMAtiZE Framework, from simple Docker deployments to production-grade Kubernetes clusters.

### Deployment Architectures Supported
- **Docker**: Single container deployment
- **Docker Compose**: Multi-service orchestration
- **Kubernetes**: Cloud-native deployment
- **Manual**: Direct installation on servers
- **PyPI**: Python package installation

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB available space
- **Python**: 3.8 or higher (for manual deployment)
- **Docker**: 20.10+ (for container deployment)
- **Kubernetes**: 1.24+ (for K8s deployment)

### API Keys Required
- **OpenAI API Key**: For AI model integrations (optional but recommended)

---

## Deployment Options

### Quick Comparison

| Method | Complexity | Scalability | Best For |
|--------|-----------|-------------|----------|
| Docker | Low | Medium | Development, Testing |
| Docker Compose | Low | Medium | Small Production |
| Kubernetes | High | High | Enterprise Production |
| Manual | Medium | Low | Custom Environments |
| PyPI | Low | N/A | Library Usage |

---

## Docker Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/makaronz/animatize.git
cd animatize

# Build Docker image
docker build -t animatize:latest .

# Run container
docker run -d \
  --name animatize \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  animatize:latest
```

### Using Pre-built Images

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/makaronz/animatize:latest

# Run the image
docker run -d \
  --name animatize \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key_here \
  ghcr.io/makaronz/animatize:latest
```

### Docker Compose Deployment

```bash
# Create .env file
cat > .env << EOF
ANIMATIZE_ENV=production
OPENAI_API_KEY=your_api_key_here
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f animatize

# Stop services
docker-compose down
```

### Using Deployment Script

```bash
# Deploy with automation
./scripts/deploy/deploy.sh deploy

# Check status
./scripts/deploy/deploy.sh status

# View logs
./scripts/deploy/deploy.sh logs

# Restart services
./scripts/deploy/deploy.sh restart
```

---

## Kubernetes Deployment

### Prerequisites
```bash
# Verify kubectl is installed
kubectl version --client

# Verify cluster access
kubectl cluster-info
```

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get all -n animatize

# View logs
kubectl logs -n animatize -l app=animatize -f

# Scale deployment
kubectl scale deployment animatize -n animatize --replicas=5
```

### Update Secrets

```bash
# Create secret from file
kubectl create secret generic animatize-secrets \
  --from-literal=OPENAI_API_KEY=your_api_key_here \
  -n animatize \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment to pick up new secrets
kubectl rollout restart deployment/animatize -n animatize
```

### Ingress Configuration (Optional)

```bash
# Create ingress for external access
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: animatize-ingress
  namespace: animatize
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - animatize.yourdomain.com
    secretName: animatize-tls
  rules:
  - host: animatize.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: animatize
            port:
              number: 80
EOF
```

---

## Manual Deployment

### Installation Steps

```bash
# Clone repository
git clone https://github.com/makaronz/animatize.git
cd animatize

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-cv.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run health checks
python scripts/deploy/health_check.py

# Start application
python src/main.py
```

### Running as a Service (systemd)

```bash
# Create service file
sudo tee /etc/systemd/system/animatize.service > /dev/null <<EOF
[Unit]
Description=ANIMAtiZE Framework
After=network.target

[Service]
Type=simple
User=animatize
WorkingDirectory=/opt/animatize
Environment="PATH=/opt/animatize/venv/bin"
ExecStart=/opt/animatize/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable animatize
sudo systemctl start animatize

# Check status
sudo systemctl status animatize
```

---

## PyPI Installation

### Install as Python Package

```bash
# Install from PyPI (when published)
pip install animatize-framework

# Install with computer vision dependencies
pip install animatize-framework[cv]

# Install for development
pip install animatize-framework[dev]

# Install all extras
pip install animatize-framework[cv,dev,monitoring]
```

### Using as Library

```python
from animatize import ANIMAtiZEFramework

# Initialize framework
framework = ANIMAtiZEFramework()

# Analyze image
result = framework.analyze_image("image.jpg")
print(result.generate_prompt())
```

---

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                 # OpenAI API key

# Optional
ANIMATIZE_ENV=production              # Environment (development/production)
LOG_LEVEL=info                        # Logging level
REDIS_HOST=localhost                  # Redis host for caching
REDIS_PORT=6379                       # Redis port
MAX_WORKERS=4                         # Number of worker processes
CACHE_TTL_HOURS=24                    # Cache TTL in hours
```

### Configuration Files

Edit `configs/*.json` files for advanced configuration:
- `configs/movement_prediction_rules.json` - Cinematic rules
- `configs/scene_analyzer.json` - CV analysis settings
- `configs/prompt_expander.json` - AI model configurations

---

## Monitoring

### Health Checks

```bash
# Manual health check
python scripts/deploy/health_check.py

# Docker health check
docker exec animatize python scripts/deploy/health_check.py

# Kubernetes health check
kubectl exec -n animatize deployment/animatize -- python scripts/deploy/health_check.py
```

### Logs

```bash
# Docker logs
docker logs -f animatize

# Docker Compose logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -n animatize -l app=animatize -f

# Manual deployment logs
tail -f logs/animatize.log
```

### Prometheus Metrics (Optional)

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Access Prometheus
open http://localhost:9090
```

---

## Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs
docker logs animatize

# Check health
docker exec animatize python scripts/deploy/health_check.py

# Verify environment variables
docker exec animatize env | grep ANIMATIZE
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

#### API Key Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('API key valid')"
```

#### Memory Issues

```bash
# Increase Docker memory limit
docker update --memory 4g animatize

# Check memory usage
docker stats animatize
```

### Getting Help

- **Documentation**: [docs.animatize.dev](https://docs.animatize.dev)
- **GitHub Issues**: [github.com/makaronz/animatize/issues](https://github.com/makaronz/animatize/issues)
- **Discord Community**: [discord.gg/animatize](https://discord.gg/animatize)
- **Email**: support@animatize.dev

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use secrets management** for production (Vault, AWS Secrets Manager)
3. **Enable TLS/SSL** for external access
4. **Run as non-root user** in containers
5. **Keep dependencies updated** regularly
6. **Enable firewall rules** to restrict access
7. **Use environment-specific configurations**
8. **Enable audit logging** for production

---

## Performance Tuning

### Docker Performance

```bash
# Adjust resource limits
docker run \
  --memory 4g \
  --cpus 2 \
  --memory-swap 6g \
  animatize:latest
```

### Kubernetes Performance

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Application Performance

```bash
# Enable caching
export ENABLE_CACHE=true
export CACHE_TTL_HOURS=24

# Adjust workers
export MAX_WORKERS=8

# Enable batch processing
export ENABLE_BATCH=true
```

---

## Backup and Recovery

### Data Backup

```bash
# Backup data directory
tar -czf animatize-backup-$(date +%Y%m%d).tar.gz data/ configs/

# Backup Docker volumes
docker run --rm \
  -v animatize_data:/backup-volume \
  -v $(pwd):/backup \
  alpine tar -czf /backup/volume-backup.tar.gz -C /backup-volume .
```

### Database Backup (if using)

```bash
# PostgreSQL backup
pg_dump -U animatize animatize_db > backup.sql

# Restore
psql -U animatize animatize_db < backup.sql
```

---

## Updates and Upgrades

### Docker Update

```bash
# Pull latest image
docker pull ghcr.io/makaronz/animatize:latest

# Restart with new image
docker-compose pull
docker-compose up -d
```

### Kubernetes Rolling Update

```bash
# Update image
kubectl set image deployment/animatize \
  animatize=ghcr.io/makaronz/animatize:v2.0.0 \
  -n animatize

# Check rollout status
kubectl rollout status deployment/animatize -n animatize
```

---

**Last Updated**: 2026-02-08  
**Version**: 1.0.0  
**Maintainer**: ANIMAtiZE Team
