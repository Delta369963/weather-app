export default function CurrentWeather({ data }) {
  if (!data) return null;

  const { location, weather, timestamp } = data;
  const iconUrl = `https://openweathermap.org/img/wn/${weather.icon}@4x.png`;

  // Format sunrise/sunset times
  const formatTime = (unix) => {
    if (!unix) return 'N/A';
    return new Date(unix * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const details = [
    { icon: '', label: 'Feels Like', value: `${Math.round(weather.feels_like)}°C` },
    { icon: '', label: 'Humidity', value: `${weather.humidity}%` },
    { icon: '', label: 'Wind Speed', value: `${weather.wind_speed} m/s` },
    { icon: '', label: 'Wind Dir', value: weather.wind_deg != null ? `${weather.wind_deg}°` : 'N/A' },
    { icon: '', label: 'Pressure', value: `${weather.pressure} hPa` },
    { icon: '', label: 'Visibility', value: weather.visibility != null ? `${(weather.visibility / 1000).toFixed(1)} km` : 'N/A' },
    { icon: '', label: 'Clouds', value: weather.clouds != null ? `${weather.clouds}%` : 'N/A' },
    { icon: '', label: 'Sunrise', value: formatTime(weather.sunrise) },
    { icon: '', label: 'Sunset', value: formatTime(weather.sunset) },
    { icon: '', label: 'Min Temp', value: `${Math.round(weather.temp_min)}°C` },
    { icon: '', label: 'Max Temp', value: `${Math.round(weather.temp_max)}°C` },
    { icon: '', label: 'Updated', value: timestamp ? new Date(timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now' },
  ];

  return (
    <div className="glass-card animate-fadeIn">
      <div className="card-title">
        <span className="icon"></span>
        Current Weather
      </div>

      <div className="weather-main">
        {/* Hero Section */}
        <div className="weather-hero">
          <div className="weather-icon-wrapper">
            <img
              className="weather-icon"
              src={iconUrl}
              alt={weather.description}
            />
          </div>
          <div>
            <div className="temperature">
              {Math.round(weather.temperature)}
              <span className="temp-unit">°C</span>
            </div>
            <div className="description">{weather.description}</div>
            <div className="location-name">
              {location.name}
              {location.state ? `, ${location.state}` : ''}
              {location.country ? ` (${location.country})` : ''}
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="weather-details-grid">
          {details.map((item, index) => (
            <div className="weather-detail-item" key={index}>
              <span className="detail-icon">{item.icon}</span>
              <div>
                <div className="detail-label">{item.label}</div>
                <div className="detail-value">{item.value}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
