#!/bin/bash

# Development Docker Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to build images
build() {
    print_status "Building Docker images..."
    docker-compose -f docker-compose.dev.yml build --no-cache
    print_status "Build completed!"
}

# Function to start services in development mode
dev() {
    print_status "Starting services in development mode..."
    check_docker
    docker-compose -f docker-compose.dev.yml up --build
}

# Function to start services in background
dev_daemon() {
    print_status "Starting services in development mode (background)..."
    check_docker
    docker-compose -f docker-compose.dev.yml up --build -d
    print_status "Services started! Check logs with: ./docker-dev.sh logs"
}

# Function to stop services
stop() {
    print_status "Stopping services..."
    docker-compose -f docker-compose.dev.yml down
    print_status "Services stopped!"
}

# Function to restart services
restart() {
    print_status "Restarting services..."
    stop
    dev_daemon
}

# Function to view logs
logs() {
    if [ -z "$2" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose -f docker-compose.dev.yml logs -f "$2"
    fi
}

# Function to clean up
clean() {
    print_warning "Cleaning up Docker containers and volumes..."
    docker-compose -f docker-compose.dev.yml down -v
    docker system prune -f
    print_status "Cleanup completed!"
}

# Function to show status
status() {
    print_status "Service status:"
    docker-compose -f docker-compose.dev.yml ps
}

# Function to enter backend shell
shell_backend() {
    print_status "Opening shell in backend container..."
    docker-compose -f docker-compose.dev.yml exec backend bash
}

# Function to enter frontend shell
shell_frontend() {
    print_status "Opening shell in frontend container..."
    docker-compose -f docker-compose.dev.yml exec frontend sh
}

# Function to show help
help() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  build          Build Docker images"
    echo "  dev            Start in development mode (foreground)"
    echo "  dev-daemon     Start in development mode (background)"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  logs [service] View logs for all services or specific service"
    echo "  clean          Stop services and clean up containers/volumes"
    echo "  status         Show service status"
    echo "  shell-backend  Open shell in backend container"
    echo "  shell-frontend Open shell in frontend container"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                # Start development environment"
    echo "  $0 logs backend       # View backend logs"
    echo "  $0 shell-backend      # SSH into backend container"
}

# Main command dispatcher
case "${1:-help}" in
    build)
        build
        ;;
    dev)
        dev
        ;;
    dev-daemon)
        dev_daemon
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$@"
        ;;
    clean)
        clean
        ;;
    status)
        status
        ;;
    shell-backend)
        shell_backend
        ;;
    shell-frontend)
        shell_frontend
        ;;
    help|*)
        help
        ;;
esac
