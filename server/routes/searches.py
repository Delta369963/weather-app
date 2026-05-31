from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from datetime import datetime
from database import searches_collection
from models import SearchCreate, SearchUpdate
from routes.weather import geocode_location
import httpx
from config import get_settings

router = APIRouter(prefix="/api/searches", tags=["Searches (CRUD)"])
settings = get_settings()


def serialize_search(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("date_from"), datetime):
        doc["date_from"] = doc["date_from"].strftime("%Y-%m-%d")
    if isinstance(doc.get("date_to"), datetime):
        doc["date_to"] = doc["date_to"].strftime("%Y-%m-%d")
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()
    return doc


async def fetch_weather_for_location(lat: float, lon: float) -> dict:
    """Fetch current weather data from OpenWeatherMap by coordinates."""
    api_key = settings.OPENWEATHER_API_KEY
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
            timeout=10.0,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        return {
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
        }


async def fetch_forecast_for_location(lat: float, lon: float) -> list:
    """Fetch 5-day forecast from OpenWeatherMap by coordinates."""
    api_key = settings.OPENWEATHER_API_KEY
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
            timeout=10.0,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        forecasts = data.get("list", [])

        daily = {}
        for item in forecasts:
            dt = item["dt_txt"].split(" ")[0]
            if dt not in daily:
                daily[dt] = {"date": dt, "temps": [], "humidity": [], "wind_speed": [], "descriptions": [], "icons": []}
            daily[dt]["temps"].append(item["main"]["temp"])
            daily[dt]["humidity"].append(item["main"]["humidity"])
            daily[dt]["wind_speed"].append(item["wind"].get("speed", 0))
            daily[dt]["descriptions"].append(item["weather"][0]["description"])
            daily[dt]["icons"].append(item["weather"][0]["icon"])

        forecast_days = []
        for dt, info in list(daily.items())[:5]:
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
        return forecast_days


# --- CREATE ---
@router.post("", status_code=201)
async def create_search(search: SearchCreate):
    """
    Create a new weather search record.
    Validates the location exists and date range is valid.
    Fetches and stores current weather + forecast data.
    """
    # Validate location by geocoding it
    try:
        geo = await geocode_location(search.location)
    except HTTPException as e:
        raise HTTPException(status_code=422, detail=f"Invalid location: {e.detail}")

    # Fetch weather data
    weather_data = await fetch_weather_for_location(geo["lat"], geo["lon"])
    forecast_data = await fetch_forecast_for_location(geo["lat"], geo["lon"])

    # Build document
    now = datetime.utcnow()
    doc = {
        "location": geo["name"],
        "location_query": search.location,
        "latitude": geo["lat"],
        "longitude": geo["lon"],
        "country": geo.get("country", ""),
        "state": geo.get("state", ""),
        "date_from": datetime.combine(search.date_from, datetime.min.time()),
        "date_to": datetime.combine(search.date_to, datetime.min.time()),
        "weather_data": weather_data,
        "forecast": forecast_data,
        "created_at": now,
        "updated_at": now,
    }

    result = await searches_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_search(doc)


# --- READ ALL ---
@router.get("")
async def list_searches(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all weather search records."""
    cursor = searches_collection.find().sort("created_at", -1).skip(skip).limit(limit)
    searches = []
    async for doc in cursor:
        searches.append(serialize_search(doc))
    return searches


# --- READ ONE ---
@router.get("/{search_id}")
async def get_search(search_id: str):
    """Get a specific weather search record by ID."""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID format.")

    doc = await searches_collection.find_one({"_id": ObjectId(search_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Search record not found.")

    return serialize_search(doc)


# --- UPDATE ---
@router.put("/{search_id}")
async def update_search(search_id: str, update: SearchUpdate):
    """
    Update a weather search record.
    If location changes, re-validates and re-fetches weather data.
    If dates change, validates the new range.
    """
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID format.")

    existing = await searches_collection.find_one({"_id": ObjectId(search_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Search record not found.")

    update_data = {}
    refetch_weather = False

    # Handle location update
    if update.location is not None:
        try:
            geo = await geocode_location(update.location)
        except HTTPException as e:
            raise HTTPException(status_code=422, detail=f"Invalid location: {e.detail}")

        update_data["location"] = geo["name"]
        update_data["location_query"] = update.location
        update_data["latitude"] = geo["lat"]
        update_data["longitude"] = geo["lon"]
        update_data["country"] = geo.get("country", "")
        update_data["state"] = geo.get("state", "")
        refetch_weather = True

    # Handle date updates
    if update.date_from is not None:
        update_data["date_from"] = datetime.combine(update.date_from, datetime.min.time())
    if update.date_to is not None:
        update_data["date_to"] = datetime.combine(update.date_to, datetime.min.time())

    # Validate date range if both dates are being set
    final_from = update_data.get("date_from", existing.get("date_from"))
    final_to = update_data.get("date_to", existing.get("date_to"))
    if final_from and final_to and final_to < final_from:
        raise HTTPException(status_code=422, detail="date_to must be after or equal to date_from.")

    # Re-fetch weather if location changed
    if refetch_weather:
        lat = update_data.get("latitude", existing.get("latitude"))
        lon = update_data.get("longitude", existing.get("longitude"))
        weather_data = await fetch_weather_for_location(lat, lon)
        forecast_data = await fetch_forecast_for_location(lat, lon)
        if weather_data:
            update_data["weather_data"] = weather_data
        if forecast_data:
            update_data["forecast"] = forecast_data

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update.")

    update_data["updated_at"] = datetime.utcnow()

    await searches_collection.update_one(
        {"_id": ObjectId(search_id)},
        {"$set": update_data},
    )

    doc = await searches_collection.find_one({"_id": ObjectId(search_id)})
    return serialize_search(doc)


# --- DELETE ---
@router.delete("/{search_id}")
async def delete_search(search_id: str):
    """Delete a weather search record."""
    if not ObjectId.is_valid(search_id):
        raise HTTPException(status_code=400, detail="Invalid search ID format.")

    result = await searches_collection.delete_one({"_id": ObjectId(search_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Search record not found.")

    return {"message": "Search record deleted successfully.", "id": search_id}
