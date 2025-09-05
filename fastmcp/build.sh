#!/bin/bash

# FastMCP Backend Build Script

set -e

echo "🚀 FastMCP Backend Build Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Setup environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your actual API keys before running the service"
fi

# Build the Docker image
print_status "Building FastMCP backend Docker image..."
docker build -t fastmcp-backend:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully!"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Start the service
print_status "Starting FastMCP backend service..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "FastMCP backend service started successfully!"
    echo ""
    echo "📋 Service Information:"
    echo "  • Backend URL: http://localhost:8000"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • API Docs: http://localhost:8000/docs (if enabled)"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Stop service: docker-compose down"
    echo "  • Shell access: docker-compose exec fastmcp-backend bash"
    echo "  • Run tests: docker-compose exec fastmcp-backend python -m pytest test/ -v"
    echo ""
    echo "📝 Next Steps:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Test the service: curl http://localhost:8000/health"
    echo "  3. Use your local CLI to connect to http://localhost:8000"
else
    print_error "Failed to start FastMCP backend service"
    exit 1
fi
