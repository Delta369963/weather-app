import { useState, useEffect } from 'react';
import { integrationsApi } from '../api';
import ErrorMessage from './ErrorMessage';

export default function YouTubeVideos({ location }) {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!location) return;
    
    const fetchVideos = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await integrationsApi.getYouTubeVideos(location);
        setVideos(data.videos || []);
      } catch (err) {
        setError(err.message);
        setVideos([]);
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [location]);

  if (!location) return null;

  return (
    <div className="glass-card animate-fadeIn" style={{ marginTop: '1.5rem' }}>
      <div className="card-title">
        <span className="icon"></span>
        YouTube Videos — {location}
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
          <div className="loading-text">Loading videos...</div>
        </div>
      ) : videos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <div className="empty-title">No videos found</div>
          <div className="empty-desc">Try searching for a different location.</div>
        </div>
      ) : (
        <div className="videos-grid">
          {videos.map((video) => (
            <a
              key={video.video_id}
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="video-card"
              id={`video-${video.video_id}`}
            >
              <img
                className="video-thumbnail"
                src={video.thumbnail}
                alt={video.title}
                loading="lazy"
              />
              <div className="video-info">
                <div className="video-title" title={video.title}>
                  {video.title}
                </div>
                <div className="video-channel">{video.channel}</div>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
