#!/bin/bash

echo "Installing ULSD Price API as a system service..."

# Stop any existing containers
echo "Stopping existing containers..."
sg docker -c "docker-compose down" 2>/dev/null || true

# Copy service file to systemd directory
sudo cp ulsd-price-api.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable ulsd-price-api.service

# Start the service now
echo "Starting service..."
sudo systemctl start ulsd-price-api.service

# Wait a moment for startup
sleep 3

# Check status
echo ""
echo "Service installed successfully!"
echo ""
echo "Checking service status:"
sudo systemctl status ulsd-price-api.service --no-pager -l

echo ""
echo "Testing API endpoint..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is responding!"
    curl -s http://localhost:8000/price | python3 -m json.tool
else
    echo "⚠️  API not responding yet. Check logs with: journalctl -u ulsd-price-api -f"
fi

echo ""
echo "Useful commands:"
echo "  sudo systemctl status ulsd-price-api   # Check status"
echo "  sudo systemctl stop ulsd-price-api     # Stop service"
echo "  sudo systemctl start ulsd-price-api    # Start service"
echo "  sudo systemctl restart ulsd-price-api  # Restart service"
echo "  sudo systemctl disable ulsd-price-api  # Disable auto-start"
echo "  journalctl -u ulsd-price-api -f        # View logs"