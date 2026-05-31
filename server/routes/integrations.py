from fastapi import APIRouter, HTTPException, Query
import httpx
from config import get_settings

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])
settings = get_settings()


@router.get("/youtube")
async def get_youtube_videos(
    location: str = Query(..., min_length=1, description="Location to search videos for"),
    max_results: int = Query(6, ge=1, le=12),
):
    """
    Search YouTube for videos about a location.
    Returns video titles, thumbnails, and watch URLs.
    """
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API key not configured.")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": f"{location} travel guide weather",
                    "type": "video",
                    "maxResults": max_results,
                    "key": api_key,
                    "order": "relevance",
                    "safeSearch": "moderate",
                },
                timeout=10.0,
            )

            if resp.status_code == 403:
                raise HTTPException(status_code=403, detail="YouTube API quota exceeded or key is invalid.")
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="YouTube service temporarily unavailable.")

            data = resp.json()
            videos = []
            for item in data.get("items", []):
                snippet = item["snippet"]
                videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": snippet["title"],
                    "description": snippet["description"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"] if "high" in snippet["thumbnails"] else snippet["thumbnails"]["default"]["url"],
                    "channel": snippet["channelTitle"],
                    "published_at": snippet["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                })

            return {"location": location, "videos": videos}

    except HTTPException:
        raise
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="YouTube service timed out.")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching YouTube videos: {str(e)}")


@router.get("/maps-embed-url")
async def get_maps_embed_url(
    location: str = Query(..., min_length=1),
    lat: float = Query(None),
    lon: float = Query(None),
):
    """
    Generate a Google Maps embed URL for a location.
    Returns the embed URL for use in an iframe.
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Maps API key not configured.")

    # Use coordinates if available, otherwise use location name
    if lat is not None and lon is not None:
        query = f"{lat},{lon}"
    else:
        query = location

    embed_url = f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={query}"

    return {
        "embed_url": embed_url,
        "location": location,
    }
