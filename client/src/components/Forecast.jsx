export default function Forecast({ data }) {
  if (!data || !data.forecast || data.forecast.length === 0) return null;

  const { location, forecast } = data;

  // Get day name from date string
  const getDayName = (dateStr) => {
    const date = new Date(dateStr + 'T12:00:00');
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) return 'Today';
    if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  const getDateLabel = (dateStr) => {
    const date = new Date(dateStr + 'T12:00:00');
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="glass-card animate-fadeIn" style={{ marginTop: '1.5rem' }}>
      <div className="card-title">
        <span className="icon"></span>
        5-Day Forecast
        <span style={{
          marginLeft: 'auto',
          fontSize: '0.8rem',
          color: 'var(--color-text-muted)',
          fontWeight: 400
        }}>
          {location.name}{location.country ? `, ${location.country}` : ''}
        </span>
      </div>

      <div className="forecast-grid">
        {forecast.map((day, index) => {
          const iconUrl = `https://openweathermap.org/img/wn/${day.icon}@2x.png`;
          return (
            <div className="forecast-card" key={index}>
              <div className="day-name">{getDayName(day.date)}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                {getDateLabel(day.date)}
              </div>
              <img
                className="forecast-icon"
                src={iconUrl}
                alt={day.description}
              />
              <div className="temp-range">
                <span className="temp-high">{Math.round(day.temp_high)}°</span>
                <span className="temp-low">{Math.round(day.temp_low)}°</span>
              </div>
              <div className="forecast-desc">{day.description}</div>
              <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '0.5rem',
                marginTop: '0.5rem',
                fontSize: '0.7rem',
                color: 'var(--color-text-muted)'
              }}>
                <span>Humidity: {day.humidity}%</span>
                <span>Wind: {day.wind_speed}m/s</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
