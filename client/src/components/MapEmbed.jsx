import { useState, useEffect } from 'react';
import { integrationsApi } from '../api';

export default function MapEmbed({ location, lat, lon }) {
  const [embedUrl, setEmbedUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!location) return;

    const fetchMapUrl = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await integrationsApi.getMapsEmbedUrl(location, lat, lon);
        setEmbedUrl(data.embed_url);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMapUrl();
  }, [location, lat, lon]);

  if (!location) return null;

  return (
    <div className="glass-card animate-fadeIn" style={{ marginTop: '1.5rem' }}>
      <div className="card-title">
        <span className="icon"></span>
        Map — {location}
      </div>

      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      ) : error ? (
        <div style={{ color: 'var(--color-text-muted)', padding: '2rem', textAlign: 'center' }}>
          <p>{error}</p>
          <p style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
            Google Maps API key may not be configured.
          </p>
        </div>
      ) : embedUrl ? (
        <div className="map-container">
          <iframe
            id="google-map-embed"
            src={embedUrl}
            title={`Map of ${location}`}
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>
      ) : null}
    </div>
  );
}
