# ULSD Futures Price API

A FastAPI-based REST API that provides current ULSD (Ultra-Low Sulfur Diesel) futures prices from TradingView with 1-hour caching.

## Features

- RESTful API endpoint for ULSD futures prices (NYMEX ATY1!)
- 1-hour caching to prevent overloading the data source
- CORS enabled for web page integration
- Health check endpoint
- Automatic cache expiration tracking

## Installation & Running

### Option 1: Docker (Recommended)

The easiest way to run the API is using Docker:

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build and run manually
docker build -t ulsd-price-api .
docker run -d -p 8000:8000 --name ulsd-price-api ulsd-price-api
```

The API will be available at `http://localhost:8000`

**Docker Commands:**
```bash
# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

**Auto-Start on Boot:**
To make the API start automatically when your system boots:
```bash
./install-service.sh
```
See [AUTO_START.md](AUTO_START.md) for detailed instructions.

### Option 2: Local Python Installation

**Prerequisites:**
- Python 3.11+ installed
- pip installed (`sudo apt-get install python3-pip` on Ubuntu/Debian)

**Install and Run:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Setup Scripts

```bash
# Setup (creates virtual environment and installs dependencies)
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run the server
./run.sh
```

## API Endpoints

### GET `/price`
Returns the current ULSD futures price with caching information.

**Response:**
```json
{
  "symbol": "ATY1!",
  "name": "ULSD 10ppm Cargoes CIF NWE (Platts) Futures",
  "exchange": "NYMEX",
  "price": 721.964,
  "currency": "USD",
  "change_percent": 0.30,
  "last_updated": "2025-11-08T12:00:00.000000",
  "source": "TradingView",
  "cached": true,
  "cache_expires_at": "2025-11-08T13:00:00.000000"
}
```

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T12:00:00.000000",
  "cache_status": "valid"
}
```

### GET `/`
API information and available endpoints.

## Using in Your Web Page

### JavaScript Fetch Example
```javascript
fetch('http://localhost:8000/price')
  .then(response => response.json())
  .then(data => {
    console.log(`Current Price: $${data.price}`);
    document.getElementById('price').textContent = `$${data.price}`;
  })
  .catch(error => console.error('Error:', error));
```

### HTML Example
```html
<!DOCTYPE html>
<html>
<head>
  <title>ULSD Price Display</title>
</head>
<body>
  <h1>ULSD Futures Price</h1>
  <div id="price-container">
    <p>Current Price: <span id="price">Loading...</span></p>
    <p>Change: <span id="change">-</span></p>
    <p>Last Updated: <span id="updated">-</span></p>
  </div>

  <script>
    async function updatePrice() {
      try {
        const response = await fetch('http://localhost:8000/price');
        const data = await response.json();

        document.getElementById('price').textContent =
          `$${data.price} ${data.currency}`;
        document.getElementById('change').textContent =
          `${data.change_percent > 0 ? '+' : ''}${data.change_percent}%`;
        document.getElementById('updated').textContent =
          new Date(data.last_updated).toLocaleString();
      } catch (error) {
        console.error('Error fetching price:', error);
        document.getElementById('price').textContent = 'Error loading price';
      }
    }

    // Update price on load
    updatePrice();

    // Refresh every 5 minutes (API caches for 1 hour)
    setInterval(updatePrice, 5 * 60 * 1000);
  </script>
</body>
</html>
```

## Caching

- Prices are cached for **1 hour** (60 minutes)
- The cache automatically refreshes after expiration
- Each response includes `cached` (true/false) and `cache_expires_at` fields
- This prevents excessive requests to TradingView

## Production Deployment

For production use:

1. **Update CORS settings** in [main.py](main.py:13-20) to specify your domain:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Use a production ASGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Set up HTTPS** using a reverse proxy (nginx/Apache) with SSL certificates

4. **Monitor the API** and adjust cache duration if needed in [main.py](main.py:20)

## Notes

- The API scrapes data from TradingView, which may change their HTML structure
- If price extraction fails, the API will return appropriate error messages
- Consider implementing authentication for production use
- Monitor rate limits if deploying publicly

## License

MIT
