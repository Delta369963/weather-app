from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date


# --- Weather Data Models ---

class WeatherData(BaseModel):
    """Weather data snapshot."""
    temperature: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_deg: Optional[int] = None
    description: str
    icon: str
    visibility: Optional[int] = None
    clouds: Optional[int] = None
    sunrise: Optional[int] = None
    sunset: Optional[int] = None


class ForecastDay(BaseModel):
    """Single day in the 5-day forecast."""
    date: str
    temp_high: float
    temp_low: float
    humidity: int
    wind_speed: float
    description: str
    icon: str


# --- CRUD Request/Response Models ---

class SearchCreate(BaseModel):
    """Request model for creating a weather search."""
    location: str = Field(..., min_length=1, max_length=200, description="Location name, zip code, or coordinates")
    date_from: date = Field(..., description="Start date for weather data")
    date_to: date = Field(..., description="End date for weather data")

    @field_validator("date_to")
    @classmethod
    def validate_date_range(cls, v, info):
        if "date_from" in info.data and v < info.data["date_from"]:
            raise ValueError("date_to must be after or equal to date_from")
        return v

    @field_validator("date_from")
    @classmethod
    def validate_date_from_not_too_old(cls, v):
        # Allow dates within a reasonable range (not older than 1 year)
        min_date = date(date.today().year - 1, 1, 1)
        if v < min_date:
            raise ValueError(f"date_from cannot be earlier than {min_date}")
        return v


class SearchUpdate(BaseModel):
    """Request model for updating a weather search."""
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    @field_validator("date_to")
    @classmethod
    def validate_date_range(cls, v, info):
        if v is not None and "date_from" in info.data and info.data["date_from"] is not None:
            if v < info.data["date_from"]:
                raise ValueError("date_to must be after or equal to date_from")
        return v


class SearchResponse(BaseModel):
    """Response model for a weather search record."""
    id: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    date_from: str
    date_to: str
    weather_data: Optional[WeatherData] = None
    forecast: Optional[list[ForecastDay]] = None
    created_at: str
    updated_at: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
