from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import httpx
from typing import Optional
import asyncio
import re

app = FastAPI(title="Commodity Pricing API", version="2.0.0")

# Add CORS middleware to allow web page requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache storage for ULSD
price_cache = {
    "data": None,
    "timestamp": None,
    "expiry_minutes": 60  # 1 hour cache
}

# Cache storage for Gold
gold_cache = {
    "data": None,
    "timestamp": None,
    "expiry_minutes": 60  # 1 hour cache
}


async def fetch_price_from_tradingview() -> dict:
    """Fetch the current price from TradingView using web scraping."""
    url = "https://tradingview.com/symbols/NYMEX-ATY1!/?timeframe=12M"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            html_content = response.text

            # Parse the price from the HTML
            # TradingView embeds price data in FAQ schema markup
            price = None
            change_percent = None

            # Look for price in FAQ schema markup
            # Pattern: "The current price of ... is 721.964 USD — it has risen 0.30%"
            schema_pattern = re.search(
                r'The current price of.*?is\s+([\d.]+)\s+USD.*?it has\s+(risen|fallen)\s+([\d.]+)%',
                html_content,
                re.IGNORECASE | re.DOTALL
            )

            if schema_pattern:
                price = float(schema_pattern.group(1))
                change_value = float(schema_pattern.group(3))
                # If it has fallen, make the change negative
                if schema_pattern.group(2).lower() == 'fallen':
                    change_percent = -change_value
                else:
                    change_percent = change_value

            # Fallback: try window.initData or other patterns
            if price is None:
                # Try to find JSON data in script tags
                json_pattern = re.search(r'"last"["\s:]+([0-9.]+)', html_content)
                if json_pattern:
                    price = float(json_pattern.group(1))

            if price is None:
                raise ValueError("Could not extract price from TradingView page")

            return {
                "symbol": "ATY1!",
                "name": "ULSD 10ppm Cargoes CIF NWE (Platts) Futures",
                "exchange": "NYMEX",
                "price": price,
                "currency": "USD",
                "change_percent": change_percent,
                "last_updated": datetime.utcnow().isoformat(),
                "source": "TradingView"
            }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch price: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing price data: {str(e)}")


def is_cache_valid() -> bool:
    """Check if the cached data is still valid."""
    if price_cache["data"] is None or price_cache["timestamp"] is None:
        return False

    expiry_time = price_cache["timestamp"] + timedelta(minutes=price_cache["expiry_minutes"])
    return datetime.utcnow() < expiry_time


async def get_cached_price() -> dict:
    """Get price from cache or fetch new data if cache is expired."""
    if is_cache_valid():
        return {
            **price_cache["data"],
            "cached": True,
            "cache_expires_at": (
                price_cache["timestamp"] + timedelta(minutes=price_cache["expiry_minutes"])
            ).isoformat()
        }

    # Cache is invalid, fetch new data
    fresh_data = await fetch_price_from_tradingview()

    # Update cache
    price_cache["data"] = fresh_data
    price_cache["timestamp"] = datetime.utcnow()

    return {
        **fresh_data,
        "cached": False,
        "cache_expires_at": (
            price_cache["timestamp"] + timedelta(minutes=price_cache["expiry_minutes"])
        ).isoformat()
    }


async def fetch_gold_price_from_bybit() -> dict:
    """Fetch the current gold price from Bybit API."""
    url = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=XAUTUSDT"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            if data.get("retCode") != 0:
                raise ValueError(f"Bybit API error: {data.get('retMsg', 'Unknown error')}")

            result = data.get("result", {}).get("list", [])
            if not result:
                raise ValueError("No data returned from Bybit API")

            ticker = result[0]

            last_price = float(ticker.get("lastPrice", 0))
            price_24h_pcnt = float(ticker.get("price24hPcnt", 0)) * 100  # Convert to percentage
            bid_price = float(ticker.get("bid1Price", 0))
            ask_price = float(ticker.get("ask1Price", 0))
            volume_24h = float(ticker.get("volume24h", 0))
            turnover_24h = float(ticker.get("turnover24h", 0))

            # Get the timestamp from Bybit API (in milliseconds)
            price_timestamp_ms = int(ticker.get("time", 0))
            # Convert milliseconds to seconds and create datetime
            price_datetime = datetime.utcfromtimestamp(price_timestamp_ms / 1000) if price_timestamp_ms else datetime.utcnow()

            return {
                "symbol": "XAUTUSDT",
                "name": "Gold (Tether Gold) Perpetual",
                "exchange": "Bybit",
                "price": last_price,
                "currency": "USDT",
                "change_percent": round(price_24h_pcnt, 4),
                "bid_price": bid_price,
                "ask_price": ask_price,
                "volume_24h": volume_24h,
                "turnover_24h_usdt": turnover_24h,
                "price_date": price_datetime.isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "source": "Bybit API"
            }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch gold price: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing gold price data: {str(e)}")


def is_gold_cache_valid() -> bool:
    """Check if the cached gold data is still valid."""
    if gold_cache["data"] is None or gold_cache["timestamp"] is None:
        return False

    expiry_time = gold_cache["timestamp"] + timedelta(minutes=gold_cache["expiry_minutes"])
    return datetime.utcnow() < expiry_time


async def get_cached_gold_price() -> dict:
    """Get gold price from cache or fetch new data if cache is expired."""
    if is_gold_cache_valid():
        return {
            **gold_cache["data"],
            "cached": True,
            "cache_expires_at": (
                gold_cache["timestamp"] + timedelta(minutes=gold_cache["expiry_minutes"])
            ).isoformat()
        }

    # Cache is invalid, fetch new data
    fresh_data = await fetch_gold_price_from_bybit()

    # Update cache
    gold_cache["data"] = fresh_data
    gold_cache["timestamp"] = datetime.utcnow()

    return {
        **fresh_data,
        "cached": False,
        "cache_expires_at": (
            gold_cache["timestamp"] + timedelta(minutes=gold_cache["expiry_minutes"])
        ).isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Commodity Pricing API",
        "version": "2.0.0",
        "endpoints": {
            "/price": "Get current ULSD futures price (cached for 1 hour)",
            "/goldprice": "Get current gold price from Bybit (cached for 1 hour)",
            "/health": "Health check endpoint"
        }
    }


@app.get("/price")
async def get_price():
    """
    Get the current ULSD futures price.
    Results are cached for 1 hour to avoid overloading the source.
    """
    return await get_cached_price()


@app.get("/goldprice")
async def get_gold_price():
    """
    Get the current gold price from Bybit.
    Results are cached for 1 hour to avoid overloading the API.
    """
    return await get_cached_gold_price()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "ulsd_cache_status": "valid" if is_cache_valid() else "expired",
        "gold_cache_status": "valid" if is_gold_cache_valid() else "expired"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
