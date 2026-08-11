#!/bin/bash

# Automated Deployment Script for Candidate Hiring Project
# This script automates the deployment process with health checks

set -e  # Exit on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/deployment_$TIMESTAMP.log"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${YELLOW}[INFO] $1${NC}" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed"
    fi
    success "Docker is installed"
    
    if ! docker compose version &> /dev/null; then
        error_exit "Docker Compose is not installed"
    fi
    success "Docker Compose is installed"
}

# Stop existing containers
stop_containers() {
    log "Stopping existing containers..."
    cd "$PROJECT_DIR"
    docker compose down || true
    success "Containers stopped"
}

# Build and start containers
build_and_start() {
    log "Building and starting containers..."
    cd "$PROJECT_DIR"
    docker compose up -d --build | tee -a "$LOG_FILE"
    success "Containers built and started"
}

# Health check function
health_check() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    
    log "Checking health of $service..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "$service is healthy"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    error_exit "$service failed health check"
}

# Display container status
show_status() {
    log "Container Status:"
    docker compose ps | tee -a "$LOG_FILE"
}

# Main deployment flow
main() {
    log "=========================================="
    log "Starting Deployment Process"
    log "=========================================="
    
    check_prerequisites
    stop_containers
    build_and_start
    
    log "Waiting for services to start..."
    sleep 10
    
    health_check "Backend API" "http://localhost:8000/docs"
    health_check "Frontend" "http://localhost:3000"
    
    show_status
    
    log "=========================================="
    log "Deployment Completed Successfully"
    log "=========================================="
    log "Frontend: http://localhost:3000"
    log "Backend API: http://localhost:8000"
    log "API Docs: http://localhost:8000/docs"
    log "Logs saved to: $LOG_FILE"
}

# Run main function
main
