# 🚀 Quick Start - Deployment

Get ANIMAtiZE Framework running in under 5 minutes!

## Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/makaronz/animatize.git
cd animatize

# Create environment file
cat > .env << EOF
ANIMATIZE_ENV=production
OPENAI_API_KEY=your_openai_api_key_here
EOF

# Deploy with automation script
./scripts/deploy/deploy.sh deploy

# Access the application
open http://localhost:8000
```

## Option 2: Docker Compose

```bash
# Clone repository
git clone https://github.com/makaronz/animatize.git
cd animatize

# Create .env file (see above)

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f animatize
```

## Option 3: Manual Installation

```bash
# Clone repository
git clone https://github.com/makaronz/animatize.git
cd animatize

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-cv.txt

# Create .env file (see above)

# Run application
python src/main.py
```

## Option 4: PyPI Installation

```bash
# Install package (when published to PyPI)
pip install animatize-framework[cv]

# Use in your code
python -c "from animatize import ANIMAtiZEFramework; print('Installed successfully!')"
```

## Verify Deployment

```bash
# Run health check
python scripts/deploy/health_check.py

# Or if using Docker
docker exec animatize python scripts/deploy/health_check.py
```

## Next Steps

- Read the [Full Deployment Guide](docs/DEPLOYMENT.md)
- Check the [Main README](README.md)
- Explore [API Documentation](docs/api/)
- Join our [Discord Community](https://discord.gg/animatize)

## Common Issues

### Port 8000 already in use
```bash
# Change port in docker-compose.yml or use different port
docker run -p 8080:8000 animatize:latest
```

### Missing API key
```bash
# Set API key in .env file
echo "OPENAI_API_KEY=your_key_here" >> .env
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Support

Need help? Check:
- [Deployment Guide](docs/DEPLOYMENT.md)
- [GitHub Issues](https://github.com/makaronz/animatize/issues)
- [Discord Community](https://discord.gg/animatize)
