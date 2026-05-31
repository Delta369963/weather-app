import { useState, useCallback } from 'react';
import SearchBar from './components/SearchBar';
import CurrentWeather from './components/CurrentWeather';
import Forecast from './components/Forecast';
import SearchHistory from './components/SearchHistory';
import YouTubeVideos from './components/YouTubeVideos';
import MapEmbed from './components/MapEmbed';
import ExportPanel from './components/ExportPanel';
import ErrorMessage from './components/ErrorMessage';
import { weatherApi, searchesApi } from './api';
import './App.css';

const TABS = [
  { key: 'weather', label: 'Weather', icon: '' },
  { key: 'history', label: 'Database', icon: '' },
  { key: 'explore', label: 'Explore', icon: '' },
  { key: 'export', label: 'Export', icon: '' },
];

function App() {
  const [activeTab, setActiveTab] = useState('weather');
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchedLocation, setSearchedLocation] = useState('');
  const [locationCoords, setLocationCoords] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Save to DB form state
  const [saveForm, setSaveForm] = useState({ dateFrom: '', dateTo: '' });
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(null);
  const [saveError, setSaveError] = useState(null);

  const handleSearch = useCallback(async (location) => {
    setLoading(true);
    setError(null);
    setCurrentWeather(null);
    setForecast(null);
    setSearchedLocation(location);
    setSaveSuccess(null);
    setSaveError(null);

    try {
      // Fetch both current weather and forecast in parallel
      const [weatherData, forecastData] = await Promise.all([
        weatherApi.getCurrent(location),
        weatherApi.getForecast(location),
      ]);

      setCurrentWeather(weatherData);
      setForecast(forecastData);
      setLocationCoords({
        lat: weatherData.location.lat,
        lon: weatherData.location.lon,
      });
      setSearchedLocation(weatherData.location.name);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSaveToDB = async (e) => {
    e.preventDefault();
    if (!searchedLocation || !saveForm.dateFrom || !saveForm.dateTo) return;

    setSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      await searchesApi.create({
        location: searchedLocation,
        date_from: saveForm.dateFrom,
        date_to: saveForm.dateTo,
      });
      setSaveSuccess('Weather data saved to database successfully!');
      setSaveForm({ dateFrom: '', dateTo: '' });
      setRefreshTrigger((prev) => prev + 1);
      setTimeout(() => setSaveSuccess(null), 4000);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <h1>Weather Hub</h1>
        <p className="subtitle">
          Real-time weather data, forecasts, and location insights
        </p>
        <div className="author-badge">
          Built by <span className="name">Nikhil Sharma</span>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav-tabs" id="main-navigation">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            id={`tab-${tab.key}`}
            className={`nav-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </nav>

      {/* Error Display */}
      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {/* Tab Content */}
      {activeTab === 'weather' && (
        <div className="animate-fadeIn">
          <SearchBar onSearch={handleSearch} loading={loading} />

          {loading && (
            <div className="loading-spinner" style={{ marginTop: '2rem' }}>
              <div className="spinner"></div>
              <div className="loading-text" style={{ marginTop: '0.75rem' }}>
                Fetching weather data...
              </div>
            </div>
          )}

          {currentWeather && <CurrentWeather data={currentWeather} />}
          {forecast && <Forecast data={forecast} />}

          {/* Save to Database Section */}
          {currentWeather && (
            <div className="glass-card animate-fadeIn" style={{ marginTop: '1.5rem' }}>
              <div className="card-title">
                <span className="icon"></span>
                Save to Database
              </div>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                Save this weather search with a date range to the database for future reference.
              </p>

              <ErrorMessage error={saveError} onDismiss={() => setSaveError(null)} />

              {saveSuccess && (
                <div style={{
                  padding: '0.75rem 1rem',
                  background: 'rgba(74, 222, 128, 0.1)',
                  border: '1px solid rgba(74, 222, 128, 0.2)',
                  borderRadius: '8px',
                  color: 'var(--color-accent-green)',
                  fontSize: '0.875rem',
                  marginBottom: '1rem',
                  animation: 'slideDown 0.3s ease',
                }}>
                  {saveSuccess}
                </div>
              )}

              <form onSubmit={handleSaveToDB}>
                <div className="date-range">
                  <div>
                    <label>From</label>
                    <input
                      type="date"
                      value={saveForm.dateFrom}
                      onChange={(e) => setSaveForm({ ...saveForm, dateFrom: e.target.value })}
                      required
                      id="save-date-from"
                    />
                  </div>
                  <div>
                    <label>To</label>
                    <input
                      type="date"
                      value={saveForm.dateTo}
                      onChange={(e) => setSaveForm({ ...saveForm, dateTo: e.target.value })}
                      min={saveForm.dateFrom || undefined}
                      required
                      id="save-date-to"
                    />
                  </div>
                  <button
                    type="submit"
                    className="btn btn-success"
                    disabled={saving || !saveForm.dateFrom || !saveForm.dateTo}
                    id="save-to-db-btn"
                  >
                    {saving ? 'Saving...' : 'Save Search'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="animate-fadeIn">
          <SearchHistory refreshTrigger={refreshTrigger} />
        </div>
      )}

      {activeTab === 'explore' && (
        <div className="animate-fadeIn">
          {searchedLocation ? (
            <>
              <MapEmbed
                location={searchedLocation}
                lat={locationCoords?.lat}
                lon={locationCoords?.lon}
              />
              <YouTubeVideos location={searchedLocation} />
            </>
          ) : (
            <div className="glass-card">
              <div className="empty-state">
                <div className="empty-icon"></div>
                <div className="empty-title">Search for a location first</div>
                <div className="empty-desc">
                  Go to the Weather tab and search for a location to see maps and videos.
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'export' && (
        <div className="animate-fadeIn">
          <ExportPanel />
        </div>
      )}

      {/* PM Accelerator Info */}
      <div className="info-banner" id="pm-accelerator-info">
        <h3>PM Accelerator</h3>
        <p>
          The Product Manager Accelerator Program is designed to support PM professionals through every stage of their career.
          From students looking for entry-level jobs to Directors looking to take on a VP role,
          our program has helped over hundreds of students. Our comprehensive approach includes
          mentorship, real-world projects, and career development resources to help you succeed
          in the competitive field of product management.
        </p>
        <p style={{ marginTop: '0.75rem' }}>
          <a href="https://www.linkedin.com/company/product-manager-accelerator/" target="_blank" rel="noopener noreferrer">
            Visit our LinkedIn Page
          </a>
        </p>
      </div>
    </div>
  );
}

export default App;
