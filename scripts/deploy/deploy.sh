#!/bin/bash
# ANIMAtiZE Framework Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_info "Prerequisites check passed ✓"
}

setup_environment() {
    log_info "Setting up environment..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env file not found. Creating from template..."
        cat > "$ENV_FILE" << EOF
# ANIMAtiZE Environment Configuration
ANIMATIZE_ENV=production
OPENAI_API_KEY=your_openai_api_key_here

# Optional Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Optional Monitoring
ENABLE_MONITORING=false
EOF
        log_warn "Please edit $ENV_FILE with your API keys before continuing."
        exit 1
    fi
    
    log_info "Environment setup complete ✓"
}

build_images() {
    log_info "Building Docker images..."
    cd "$PROJECT_ROOT"
    
    docker-compose build --no-cache
    
    log_info "Docker images built successfully ✓"
}

start_services() {
    log_info "Starting services..."
    cd "$PROJECT_ROOT"
    
    # Load environment variables
    set -a
    source "$ENV_FILE"
    set +a
    
    # Start services
    docker-compose up -d
    
    log_info "Services started successfully ✓"
}

check_health() {
    log_info "Checking service health..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T animatize python scripts/deploy/health_check.py &> /dev/null; then
            log_info "Health check passed ✓"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log_info "Waiting for services to be healthy... ($attempt/$max_attempts)"
        sleep 2
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    echo ""
    log_info "Logs (last 20 lines):"
    docker-compose logs --tail=20 animatize
    
    echo ""
    log_info "Access the application at: http://localhost:8000"
}

stop_services() {
    log_info "Stopping services..."
    cd "$PROJECT_ROOT"
    docker-compose down
    log_info "Services stopped ✓"
}

restart_services() {
    log_info "Restarting services..."
    stop_services
    start_services
    check_health
}

show_logs() {
    cd "$PROJECT_ROOT"
    docker-compose logs -f animatize
}

# Main script
main() {
    cd "$PROJECT_ROOT"
    
    case "${1:-deploy}" in
        deploy)
            log_info "🚀 Starting deployment..."
            check_prerequisites
            setup_environment
            build_images
            start_services
            check_health
            show_status
            log_info "✅ Deployment complete!"
            ;;
        start)
            start_services
            check_health
            show_status
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        build)
            build_images
            ;;
        health)
            check_health
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|status|logs|build|health}"
            exit 1
            ;;
    esac
}

main "$@"
