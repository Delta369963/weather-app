from fastapi import APIRouter, HTTPException, Query
import httpx
from config import get_settings

router = APIRouter(prefix="/api/weather", tags=["Weather"])
settings = get_settings()

OPENWEATHER_BASE = "https://api.openweathermap.org"


async def geocode_location(location: str) -> dict:
    """
    Geocode a location string to lat/lon.
    Supports: city name, zip code, coordinates, landmarks.
    Returns dict with lat, lon, name, country.
    """
    api_key = settings.OPENWEATHER_API_KEY

    # Check if input looks like coordinates (lat,lon)
    if "," in location:
        parts = location.split(",")
        if len(parts) == 2:
            try:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    # Reverse geocode to get location name
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(
                            f"{OPENWEATHER_BASE}/geo/1.0/reverse",
                            params={"lat": lat, "lon": lon, "limit": 1, "appid": api_key},
                            timeout=10.0,
                        )
                        if resp.status_code == 200 and resp.json():
                            data = resp.json()[0]
                            return {
                                "lat": lat,
                                "lon": lon,
                                "name": data.get("name", f"{lat},{lon}"),
                                "country": data.get("country", ""),
                                "state": data.get("state", ""),
                            }
                        return {"lat": lat, "lon": lon, "name": f"{lat},{lon}", "country": "", "state": ""}
            except ValueError:
                pass

    # Check if input looks like a zip/postal code (digits, possibly with country code)
    clean = location.strip()
    if clean.replace("-", "").replace(" ", "").isdigit() or (
        len(clean.split(",")) == 2 and clean.split(",")[0].strip().replace("-", "").replace(" ", "").isdigit()
    ):
        async with httpx.AsyncClient() as client:
            # Try zip code geocoding
            zip_query = clean if "," in clean else f"{clean},US"
            resp = await client.get(
                f"{OPENWEATHER_BASE}/geo/1.0/zip",
                params={"zip": zip_query, "appid": api_key},
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "lat": data["lat"],
                    "lon": data["lon"],
                    "name": data.get("name", clean),
                    "country": data.get("country", ""),
                    "state": "",
                }

    # Default: direct geocoding by name (city, landmark, etc.)
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{OPENWEATHER_BASE}/geo/1.0/direct",
            params={"q": location, "limit": 1, "appid": api_key},
            timeout=10.0,
        )
        if resp.status_code == 200 and resp.json():
            data = resp.json()[0]
            return {
                "lat": data["lat"],
                "lon": data["lon"],
                "name": data.get("name", location),
                "country": data.get("country", ""),
                "state": data.get("state", ""),
            }

    raise HTTPException(
        status_code=404,
        detail=f"Location '{location}' not found. Please check the spelling or try a different format (city name, zip code, or coordinates).",
    )


@router.get("/geocode")
async def geocode(location: str = Query(..., min_length=1, description="Location to geocode")):
    """Geocode a location string and return coordinates + resolved name."""
    geo = await geocode_location(location)
    return geo


@router.get("/current")
async def get_current_weather(location: str = Query(..., min_length=1)):
    """Get current weather for a location."""
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeatherMap API key not configured.")

    try:
        geo = await geocode_location(location)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {str(e)}")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{OPENWEATHER_BASE}/data/2.5/weather",
                params={
                    "lat": geo["lat"],
                    "lon": geo["lon"],
                    "appid": api_key,
                    "units": "metric",
                },
                timeout=10.0,
            )

            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid OpenWeatherMap API key.")
            if resp.status_code == 429:
                raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again shortly.")
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Weather service temporarily unavailable.")

            data = resp.json()
            weather = data["weather"][0]
            main = data["main"]
            wind = data.get("wind", {})
            sys = data.get("sys", {})

            return {
                "location": {
                    "name": geo["name"],
                    "country": geo["country"],
                    "state": geo.get("state", ""),
                    "lat": geo["lat"],
                    "lon": geo["lon"],
                },
                "weather": {
                    "temperature": main["temp"],
                    "feels_like": main["feels_like"],
                    "temp_min": main["temp_min"],
                    "temp_max": main["temp_max"],
                    "humidity": main["humidity"],
                    "pressure": main["pressure"],
                    "wind_speed": wind.get("speed", 0),
                    "wind_deg": wind.get("deg"),
                    "description": weather["description"],
                    "icon": weather["icon"],
                    "visibility": data.get("visibility"),
                    "clouds": data.get("clouds", {}).get("all"),
                    "sunrise": sys.get("sunrise"),
                    "sunset": sys.get("sunset"),
                },
                "timestamp": data.get("dt"),
            }

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Weather service timed out. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching weather data: {str(e)}")


@router.get("/forecast")
async def get_forecast(location: str = Query(..., min_length=1)):
    """Get 5-day weather forecast for a location."""
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeatherMap API key not configured.")

    try:
        geo = await geocode_location(location)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Geocoding service error: {str(e)}")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{OPENWEATHER_BASE}/data/2.5/forecast",
                params={
                    "lat": geo["lat"],
                    "lon": geo["lon"],
                    "appid": api_key,
                    "units": "metric",
                },
                timeout=10.0,
            )

            if resp.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid OpenWeatherMap API key.")
            if resp.status_code == 429:
                raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again shortly.")
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Weather service temporarily unavailable.")

            data = resp.json()
            forecasts = data.get("list", [])

            # Group by day and get daily summary
            daily = {}
            for item in forecasts:
                dt = item["dt_txt"].split(" ")[0]
                if dt not in daily:
                    daily[dt] = {
                        "date": dt,
                        "temps": [],
                        "humidity": [],
                        "wind_speed": [],
                        "descriptions": [],
                        "icons": [],
                    }
                daily[dt]["temps"].append(item["main"]["temp"])
                daily[dt]["humidity"].append(item["main"]["humidity"])
                daily[dt]["wind_speed"].append(item["wind"].get("speed", 0))
                daily[dt]["descriptions"].append(item["weather"][0]["description"])
                daily[dt]["icons"].append(item["weather"][0]["icon"])

            # Build 5-day forecast
            forecast_days = []
            for dt, info in list(daily.items())[:5]:
                # Pick the most common description and icon (midday preference)
                mid_idx = len(info["descriptions"]) // 2
                forecast_days.append({
                    "date": dt,
                    "temp_high": round(max(info["temps"]), 1),
                    "temp_low": round(min(info["temps"]), 1),
                    "humidity": round(sum(info["humidity"]) / len(info["humidity"])),
                    "wind_speed": round(sum(info["wind_speed"]) / len(info["wind_speed"]), 1),
                    "description": info["descriptions"][mid_idx],
                    "icon": info["icons"][mid_idx],
                })

            return {
                "location": {
                    "name": geo["name"],
                    "country": geo["country"],
                    "state": geo.get("state", ""),
                    "lat": geo["lat"],
                    "lon": geo["lon"],
                },
                "forecast": forecast_days,
            }

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Weather service timed out. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching forecast data: {str(e)}")
