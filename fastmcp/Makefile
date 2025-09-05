# FastMCP Backend Makefile for Docker Operations

.PHONY: help build run stop logs shell test clean

# Default target
help: ## Show this help message
	@echo "FastMCP Backend Docker Operations"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
setup: ## Setup environment file from example
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from env.example"; \
		echo "Please edit .env with your actual API keys"; \
	else \
		echo ".env file already exists"; \
	fi

# Build operations
build: ## Build Docker image
	docker build -t fastmcp-backend:latest .

# Run operations
run: ## Start the backend service
	docker-compose up -d

run-build: ## Build and start the backend service
	docker-compose up -d --build

run-logs: ## Start with logs visible
	docker-compose up

# Stop operations
stop: ## Stop the backend service
	docker-compose down

# Logs
logs: ## View logs
	docker-compose logs -f

# Shell access
shell: ## Open shell in container
	docker-compose exec fastmcp-backend bash

# Testing
test: ## Run tests
	docker-compose exec fastmcp-backend python -m pytest test/ -v

test-coverage: ## Run tests with coverage
	docker-compose exec fastmcp-backend python -m pytest test/ --cov=app --cov-report=html

# Health check
health: ## Check application health
	curl -f http://localhost:8000/health || echo "Health check failed"

# Status
status: ## Show container status
	docker-compose ps

# Cleanup
clean: ## Stop and remove containers
	docker-compose down

clean-images: ## Remove Docker images
	docker rmi fastmcp-backend:latest || true

clean-all: clean clean-images ## Remove everything

# Quick start
quickstart: setup run-build ## Quick start for new users
	@echo ""
	@echo "FastMCP Backend is starting up!"
	@echo "==============================="
	@echo ""
	@echo "1. Edit .env file with your API keys"
	@echo "2. Backend will be available at: http://localhost:8000"
	@echo "3. Health check: http://localhost:8000/health"
	@echo "4. View logs with: make logs"
	@echo "5. Stop with: make stop"
	@echo ""
