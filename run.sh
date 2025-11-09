#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Warning: Virtual environment not found. Run ./setup.sh first."
    echo "Attempting to run with system Python..."
fi

# Start the API server
echo "Starting ULSD Futures Price API on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 main.py