# Troubleshooting Guide

## Service Installation Issues

### "KeyError: ContainerConfig" Error

This error occurs when there's a conflicting Docker container.

**Solution:**
```bash
# Stop any existing containers
sg docker -c "docker-compose down"

# Clean up Docker resources
sg docker -c "docker system prune -f"

# Then run the install script again
./install-service.sh
```

### Service Won't Start

**Check the logs:**
```bash
journalctl -u ulsd-price-api -n 50 --no-pager
```

**Common issues:**

1. **Docker not running:**
   ```bash
   sudo systemctl status docker
   sudo systemctl start docker
   ```

2. **Permission issues:**
   ```bash
   # Make sure you're in the docker group
   groups | grep docker

   # If not, add yourself
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Port already in use:**
   ```bash
   # Check if something is using port 8000
   sudo netstat -tlnp | grep 8000

   # Or with ss
   sudo ss -tlnp | grep 8000
   ```

### Manual Start (Without Service)

If the service won't start, you can run manually:

```bash
# Stop the service first
sudo systemctl stop ulsd-price-api

# Run manually
sg docker -c "docker-compose up -d"

# Check if it works
curl http://localhost:8000/price
```

### Rebuild Container After Code Changes

```bash
# If using service
sudo systemctl stop ulsd-price-api
sg docker -c "docker-compose down"
sg docker -c "docker-compose up -d --build"
sudo systemctl start ulsd-price-api

# Or manually
sg docker -c "docker-compose down"
sg docker -c "docker-compose up -d --build"
```

## API Issues

### Price Not Loading

**Check the logs:**
```bash
sg docker -c "docker-compose logs -f"
```

**Test the endpoint:**
```bash
curl -v http://localhost:8000/price
```

**Common issues:**

1. **TradingView blocked the request:**
   - The scraper might be rate-limited
   - Wait a few minutes and try again
   - Check logs for HTTP errors

2. **Network issues:**
   ```bash
   # Test if you can reach TradingView
   curl -I https://tradingview.com
   ```

3. **HTML structure changed:**
   - TradingView may have updated their page
   - Check the logs for "Could not extract price" errors
   - May need to update the regex patterns in main.py

### Cache Not Working

**Check cache status:**
```bash
curl http://localhost:8000/health
```

Look for `"cache_status": "valid"` or `"cache_status": "expired"`

**Force cache refresh:**
- Wait for cache to expire (1 hour)
- Or restart the container: `sg docker -c "docker-compose restart"`

## Docker Issues

### Container Keeps Restarting

```bash
# Check container status
sg docker -c "docker ps -a"

# View logs
sg docker -c "docker-compose logs --tail=100"
```

### Out of Disk Space

```bash
# Clean up unused Docker resources
sg docker -c "docker system prune -a"

# Remove unused volumes
sg docker -c "docker volume prune"
```

### Can't Connect to Docker Daemon

```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker on boot
sudo systemctl enable docker
```

## Testing Tools

### Test API from Command Line

```bash
# Health check
curl http://localhost:8000/health

# Get price
curl http://localhost:8000/price

# Pretty JSON
curl -s http://localhost:8000/price | python3 -m json.tool

# With verbose output
curl -v http://localhost:8000/price
```

### Check if Port is Accessible

```bash
# From local machine
curl http://localhost:8000/price

# From network (replace with your IP)
curl http://192.168.x.x:8000/price

# Check if port is listening
sudo netstat -tlnp | grep 8000
```

## Getting Help

If you're still having issues:

1. **Collect logs:**
   ```bash
   # Service logs
   journalctl -u ulsd-price-api -n 100 --no-pager > service-logs.txt

   # Container logs
   sg docker -c "docker-compose logs" > container-logs.txt
   ```

2. **Check versions:**
   ```bash
   docker --version
   docker-compose --version
   python3 --version
   ```

3. **Test without Docker:**
   ```bash
   # Stop Docker version
   sudo systemctl stop ulsd-price-api
   sg docker -c "docker-compose down"

   # Install dependencies
   pip3 install -r requirements.txt

   # Run directly
   python3 main.py
   ```

## Reset Everything

If you want to start fresh:

```bash
# Stop and disable service
sudo systemctl stop ulsd-price-api
sudo systemctl disable ulsd-price-api
sudo rm /etc/systemd/system/ulsd-price-api.service
sudo systemctl daemon-reload

# Remove all containers and images
sg docker -c "docker-compose down -v"
sg docker -c "docker system prune -a"

# Start over
./install-service.sh
```