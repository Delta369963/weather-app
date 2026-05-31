from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import ping_db
from routes import weather, searches, integrations, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    db_ok = await ping_db()
    if db_ok:
        print("Connected to MongoDB successfully")
    else:
        print("MongoDB connection failed — app will start but DB operations may fail")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Weather App API",
    description="Full-stack weather application with CRUD, 5-day forecast, and integrations. Built by Nikhil Sharma.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(weather.router)
app.include_router(searches.router)
app.include_router(integrations.router)
app.include_router(export.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Weather App API",
        "version": "1.0.0",
        "author": "Nikhil Sharma",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    db_ok = await ping_db()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }
