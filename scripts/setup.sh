#!/bin/bash

# Macro-Man MCP Server Setup Script
# This script sets up the development environment for the MCP server

set -e

echo "🚀 Setting up Macro-Man MCP Server..."

# Check if Python 3.11 is available
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Found Python 3.11"
elif command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    required_version="3.10"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        echo "❌ Python 3.10+ is required. Current version: $python_version"
        echo "💡 Install Python 3.11 with: brew install python@3.11"
        exit 1
    fi
    
    PYTHON_CMD="python3"
    echo "✅ Python version check passed: $python_version"
else
    echo "❌ Python 3.10+ is required but not found"
    echo "💡 Install Python 3.11 with: brew install python@3.11"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the server"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
python -m pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit .env file with your configuration"
echo "3. Run: python main.py"
echo ""
echo "To run tests:"
echo "python -m pytest tests/ -v"
echo ""
echo "To format code:"
echo "black src/ tests/"
echo "isort src/ tests/"
