#!/bin/bash
# TrueMesh Provider Intelligence - Quick Start Script

set -e

echo "=========================================="
echo "  TrueMesh Provider Intelligence"
echo "  Quick Start Deployment"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and set your SECRET_KEY and ENCRYPTION_KEY"
    echo "   You can generate secure keys with:"
    echo "   python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/models
echo "✓ Data directories created"
echo ""

# Start services
echo "🚀 Starting TrueMesh services..."
echo ""
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "=========================================="
echo "  ✅ TrueMesh is now running!"
echo "=========================================="
echo ""
echo "🌐 Access Points:"
echo "  - API Documentation: http://localhost:8000/docs"
echo "  - Health Check: http://localhost:8000/health"
echo "  - Admin API: http://localhost:8000/api/v1/admin/stats/overview"
echo ""
echo "📋 Useful Commands:"
echo "  - View logs: docker-compose logs -f app"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
echo "📚 See README.md for full documentation"
echo "=========================================="
