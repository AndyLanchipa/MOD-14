#!/bin/bash

# Local development script
echo "Setting up Calculation API development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest tests/ -v

echo "Development environment ready!"
echo "Run 'source venv/bin/activate' to activate the virtual environment"
echo "Run 'uvicorn main:app --reload' to start the development server"