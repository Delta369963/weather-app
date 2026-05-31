from motor.motor_asyncio import AsyncIOMotorClient
from config import get_settings

settings = get_settings()

# MongoDB client and database
client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

# Collections
searches_collection = db["weather_searches"]


async def ping_db():
    """Test database connection."""
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
