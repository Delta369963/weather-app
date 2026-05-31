import { useState } from 'react';

export default function SearchBar({ onSearch, loading }) {
  const [location, setLocation] = useState('');
  const [geoLoading, setGeoLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (location.trim()) {
      onSearch(location.trim());
    }
  };

  const handleGeolocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }

    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const coords = `${latitude.toFixed(4)},${longitude.toFixed(4)}`;
        setLocation(coords);
        onSearch(coords);
        setGeoLoading(false);
      },
      (error) => {
        setGeoLoading(false);
        let msg = 'Unable to get your location.';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            msg = 'Location access denied. Please enable location permissions in your browser.';
            break;
          case error.POSITION_UNAVAILABLE:
            msg = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            msg = 'Location request timed out. Please try again.';
            break;
        }
        alert(msg);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  return (
    <div className="search-section glass-card">
      <div className="card-title">
        <span className="icon"></span>
        Search Weather
      </div>
      <form onSubmit={handleSubmit}>
        <div className="search-container">
          <div className="search-input-wrapper">
            <span className="search-icon"></span>
            <input
              id="location-search-input"
              type="text"
              className="search-input"
              placeholder="Enter city, zip code, coordinates, or landmark..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={loading}
              aria-label="Location search"
            />
          </div>
          <button
            id="search-weather-btn"
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={loading || !location.trim()}
          >
            {loading ? (
              <>
                <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span>
                Searching...
              </>
            ) : (
              <>Get Weather</>
            )}
          </button>
          <button
            id="geolocation-btn"
            type="button"
            className="btn btn-secondary btn-lg"
            onClick={handleGeolocation}
            disabled={loading || geoLoading}
            title="Use current location"
          >
            {geoLoading ? (
              <>
                <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }}></span>
                Locating...
              </>
            ) : (
              <>My Location</>
            )}
          </button>
        </div>
      </form>
      <p style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
        Supports: City names (New York), Zip codes (10001), GPS coordinates (40.71,-74.00), Landmarks (Eiffel Tower)
      </p>
    </div>
  );
}
