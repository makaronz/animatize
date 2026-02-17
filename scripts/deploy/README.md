# Deployment Scripts

This directory contains scripts for deploying the ANIMAtiZE Framework.

## Available Scripts

### deploy.sh
Main deployment automation script.

**Usage:**
```bash
# Full deployment
./scripts/deploy/deploy.sh deploy

# Start services
./scripts/deploy/deploy.sh start

# Stop services
./scripts/deploy/deploy.sh stop

# Restart services
./scripts/deploy/deploy.sh restart

# View status
./scripts/deploy/deploy.sh status

# View logs
./scripts/deploy/deploy.sh logs

# Build images only
./scripts/deploy/deploy.sh build

# Health check
./scripts/deploy/deploy.sh health
```

### health_check.py
Health check script to verify system readiness.

**Usage:**
```bash
# Run health check
python scripts/deploy/health_check.py

# Run in Docker
docker exec animatize python scripts/deploy/health_check.py

# Run in Kubernetes
kubectl exec -n animatize deployment/animatize -- python scripts/deploy/health_check.py
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/makaronz/animatize.git
   cd animatize
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Deploy**
   ```bash
   ./scripts/deploy/deploy.sh deploy
   ```

4. **Verify**
   ```bash
   ./scripts/deploy/deploy.sh status
   ./scripts/deploy/deploy.sh health
   ```

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.8+ (for health checks)
- Bash shell

## Configuration

Edit `.env` file before deployment:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANIMATIZE_ENV`: Environment (development/production)
- Other optional settings

## Troubleshooting

### Deployment fails
```bash
# Check logs
./scripts/deploy/deploy.sh logs

# Check Docker status
docker ps -a

# Rebuild and redeploy
./scripts/deploy/deploy.sh build
./scripts/deploy/deploy.sh restart
```

### Health check fails
```bash
# Run detailed health check
python scripts/deploy/health_check.py

# Check Python dependencies
pip install -r requirements.txt
```

### Port already in use
```bash
# Change port in docker-compose.yml
# Default is 8000, change to something else like 8080
```

## Support

For more information, see:
- [Full Deployment Guide](../../docs/DEPLOYMENT.md)
- [Main README](../../README.md)
- [GitHub Issues](https://github.com/makaronz/animatize/issues)
