# Auto-Start Configuration Guide

This guide explains how to make the ULSD Price API start automatically when your system boots.

## Quick Setup

Run the installation script:

```bash
./install-service.sh
```

This will install and enable the systemd service that starts the API automatically on boot.

## Manual Setup (Alternative)

If you prefer to set it up manually:

### Step 1: Copy the service file

```bash
sudo cp ulsd-price-api.service /etc/systemd/system/
```

### Step 2: Reload systemd

```bash
sudo systemctl daemon-reload
```

### Step 3: Enable auto-start

```bash
sudo systemctl enable ulsd-price-api.service
```

### Step 4: Start the service now

```bash
sudo systemctl start ulsd-price-api.service
```

### Step 5: Verify it's running

```bash
sudo systemctl status ulsd-price-api.service
```

## Managing the Service

### Check Status
```bash
sudo systemctl status ulsd-price-api
```

### Start Service
```bash
sudo systemctl start ulsd-price-api
```

### Stop Service
```bash
sudo systemctl stop ulsd-price-api
```

### Restart Service
```bash
sudo systemctl restart ulsd-price-api
```

### Enable Auto-Start (on boot)
```bash
sudo systemctl enable ulsd-price-api
```

### Disable Auto-Start
```bash
sudo systemctl disable ulsd-price-api
```

### View Logs
```bash
# View service logs
journalctl -u ulsd-price-api -f

# View Docker container logs
sg docker -c "docker-compose logs -f"
```

## How It Works

The systemd service:
1. Waits for Docker to be ready
2. Runs `docker-compose up -d` in your project directory
3. The container has `restart: unless-stopped` policy, so it will:
   - Restart automatically if it crashes
   - Start automatically when Docker starts
   - Survive system reboots

## Testing Auto-Start

To test that auto-start works:

1. Enable the service: `sudo systemctl enable ulsd-price-api`
2. Reboot your system: `sudo reboot`
3. After reboot, check if it's running: `curl http://localhost:8000/price`

## Alternative: Docker-Only Auto-Start

If you don't want to use systemd, you can rely on Docker's restart policy:

1. Make sure your user is in the docker group:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. Enable Docker to start on boot:
   ```bash
   sudo systemctl enable docker
   ```

3. Start the container with restart policy:
   ```bash
   docker-compose up -d
   ```

The `restart: unless-stopped` in [docker-compose.yml](docker-compose.yml) ensures the container starts automatically when Docker starts.

## Troubleshooting

### Service fails to start
Check the logs:
```bash
journalctl -u ulsd-price-api -n 50
```

### Container doesn't start
Check Docker logs:
```bash
sg docker -c "docker-compose logs"
```

### Permission issues
Ensure your user is in the docker group:
```bash
groups | grep docker
```

If not, add yourself:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Uninstalling the Service

To remove the auto-start service:

```bash
# Stop and disable the service
sudo systemctl stop ulsd-price-api
sudo systemctl disable ulsd-price-api

# Remove the service file
sudo rm /etc/systemd/system/ulsd-price-api.service

# Reload systemd
sudo systemctl daemon-reload
```

The Docker container will continue running until you stop it manually with:
```bash
docker-compose down
```