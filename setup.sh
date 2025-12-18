#!/bin/bash

# EventKit Agent - Quick Setup Script
# This script sets up the development environment from scratch

set -e  # Exit on any error

echo "=========================================="
echo "EventKit Agent - Environment Setup"
echo "=========================================="
echo ""

# Check Python version
echo "→ Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "→ Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "→ Upgrading pip..."
python -m pip install --upgrade pip -q
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "→ Installing production dependencies..."
pip install -r requirements.txt -q
echo "✓ Production dependencies installed"
echo ""

echo "→ Installing development dependencies..."
pip install -r requirements-dev.txt -q
echo "✓ Development dependencies installed"
echo ""

# Install pre-commit hooks
echo "→ Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✓ Pre-commit hooks installed"
else
    echo "⚠ pre-commit not found, skipping hook installation"
fi
echo ""

# Create necessary directories
echo "→ Creating data directories..."
mkdir -p data/logs data/exports data/profiles
echo "✓ Data directories created"
echo ""

# Copy .env.example if .env doesn't exist
if [ ! -f "deploy/.env" ]; then
    echo "→ Creating .env file from template..."
    cp deploy/.env.example deploy/.env
    echo "✓ .env file created (remember to update with your credentials)"
else
    echo "✓ .env file already exists"
fi
echo ""

# Run tests to verify setup
echo "→ Running tests to verify setup..."
if pytest -v --tb=short; then
    echo "✓ All tests passed!"
else
    echo "⚠ Some tests failed, but setup is complete"
fi
echo ""

echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Update deploy/.env with your credentials"
echo "  2. Run 'make run' to start the agent server"
echo "  3. Run 'make test' to run tests"
echo "  4. Run 'make help' to see all available commands"
echo ""
echo "For Docker deployment:"
echo "  - Run 'make docker-build' to build the image"
echo "  - Run 'make docker-run' to start the container"
echo ""
