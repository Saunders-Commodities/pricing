#!/bin/bash

echo "Setting up ULSD Futures Price API..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python 3 found: $(python3 --version)"

# Install pip if not available
if ! python3 -m pip --version &> /dev/null; then
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To start the API server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the server: python main.py"
echo "  3. Open index.html in your web browser"
echo ""
