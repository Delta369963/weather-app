# Weather Hub — Full Stack Weather Application

> Built by **Nikhil Sharma** for the PM Accelerator Technical Assessment

A full-stack weather application providing real-time weather data, 5-day forecasts, database persistence with CRUD operations, YouTube video integration, Google Maps embedding, and multi-format data export.

## Features

### Frontend (Tech Assessment #1)
- **Location Search**: Supports city names, zip codes, GPS coordinates, and landmarks
- **Current Location**: Browser geolocation for instant local weather
- **Current Weather**: Temperature, humidity, wind, pressure, visibility, sunrise/sunset
- **5-Day Forecast**: Daily high/low temps, weather icons, humidity, wind speed
- **Error Handling**: Graceful handling of invalid locations, API failures, network issues
- **Responsive Design**: Desktop, tablet, and mobile layouts
- **Modern UI**: Dark theme with glassmorphism, gradients, and animations

### Backend (Tech Assessment #2)
- **CRUD Operations**: Full Create, Read, Update, Delete for weather searches
  - CREATE: Validates location + date range, fetches and stores weather data
  - READ: View all saved searches or a specific record
  - UPDATE: Edit location/dates with re-validation and weather re-fetch
  - DELETE: Remove records with confirmation
- **API Integrations**: YouTube videos and Google Maps for searched locations
- **Data Export**: JSON, CSV, XML, Markdown, and PDF export formats
- **Input Validation**: Date range validation, location verification via geocoding

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 19 + Vite |
| Backend | Python FastAPI |
| Database | MongoDB (via Motor async driver) |
| Weather API | OpenWeatherMap |
| Videos | YouTube Data API v3 |
| Maps | Google Maps Embed API |
| Styling | Vanilla CSS (dark glassmorphism theme) |

## Setup & Installation

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.9+
- **MongoDB** (local or [MongoDB Atlas](https://www.mongodb.com/atlas) free tier)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/Weather-App.git
cd Weather-App
```

### 2. Get API Keys (all free)

| API | Sign Up | Free Tier |
|-----|---------|-----------|
| OpenWeatherMap | [openweathermap.org/api](https://openweathermap.org/api) | 1,000 calls/day |
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com/) | 10,000 units/day |
| Google Maps Embed API | Same Google Cloud project | Unlimited embeds |

### 3. Backend Setup
```bash
cd server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB URI

# Run the server
uvicorn main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd client

# Install dependencies
npm install

# Run the dev server
npm run dev
```

### 5. Open the app
- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

```
Weather-App/
├── client/                   # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx       # Location search with geolocation
│   │   │   ├── CurrentWeather.jsx  # Current weather display
│   │   │   ├── Forecast.jsx        # 5-day forecast
│   │   │   ├── SearchHistory.jsx   # CRUD table with edit/delete
│   │   │   ├── YouTubeVideos.jsx   # YouTube video grid
│   │   │   ├── MapEmbed.jsx        # Google Maps embed
│   │   │   ├── ExportPanel.jsx     # Data export buttons
│   │   │   └── ErrorMessage.jsx    # Error display
│   │   ├── api.js                  # API client
│   │   ├── App.jsx                 # Main app with routing
│   │   └── index.css               # Design system
│   └── index.html
│
├── server/                   # FastAPI Backend
│   ├── routes/
│   │   ├── weather.py        # Weather + geocoding endpoints
│   │   ├── searches.py       # CRUD endpoints
│   │   ├── integrations.py   # YouTube + Maps endpoints
│   │   └── export.py         # Data export (JSON/CSV/XML/MD/PDF)
│   ├── main.py               # FastAPI app
│   ├── config.py             # Environment configuration
│   ├── database.py           # MongoDB connection
│   ├── models.py             # Pydantic models
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment template
│
├── .gitignore
├── README.md
└── Task.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather/current?location=...` | Current weather |
| GET | `/api/weather/forecast?location=...` | 5-day forecast |
| GET | `/api/weather/geocode?location=...` | Geocode location |
| POST | `/api/searches` | Create search record |
| GET | `/api/searches` | List all searches |
| GET | `/api/searches/{id}` | Get specific search |
| PUT | `/api/searches/{id}` | Update search |
| DELETE | `/api/searches/{id}` | Delete search |
| GET | `/api/integrations/youtube?location=...` | YouTube videos |
| GET | `/api/integrations/maps-embed-url?location=...` | Maps embed URL |
| GET | `/api/export/{format}` | Export data (json/csv/xml/markdown/pdf) |

## Design

The app uses a modern dark theme with:
- **Glassmorphism** cards with backdrop blur
- **Gradient** accents (sky/aurora/sunset themes)
- **Inter** font family
- **Micro-animations** (float, fade, slide)
- **Responsive** CSS Grid and Flexbox layouts

## About PM Accelerator

The Product Manager Accelerator Program is designed to support PM professionals through every stage of their career. From students looking for entry-level jobs to Directors looking to take on a VP role, our program has helped hundreds of students with mentorship, real-world projects, and career development resources.

[LinkedIn: Product Manager Accelerator](https://www.linkedin.com/company/product-manager-accelerator/)

---

**Built by Nikhil Sharma**
