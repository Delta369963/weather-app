import { useState } from 'react';
import { exportApi } from '../api';
import ErrorMessage from './ErrorMessage';

const FORMATS = [
  { key: 'json', label: 'JSON', icon: '', color: '#fbbf24' },
  { key: 'csv', label: 'CSV', icon: '', color: '#4ade80' },
  { key: 'xml', label: 'XML', icon: '', color: '#f472b6' },
  { key: 'markdown', label: 'Markdown', icon: '', color: '#a78bfa' },
  { key: 'pdf', label: 'PDF', icon: '', color: '#f87171' },
];

export default function ExportPanel() {
  const [loading, setLoading] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleExport = async (format) => {
    setLoading(format);
    setError(null);
    setSuccess(null);
    try {
      await exportApi.downloadFile(format);
      setSuccess(`Successfully exported as ${format.toUpperCase()}`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="glass-card animate-fadeIn">
      <div className="card-title">
        <span className="icon"></span>
        Export Data
      </div>
      <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
        Export all saved weather search records from the database in your preferred format.
      </p>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {success && (
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
          {success}
        </div>
      )}

      <div className="export-buttons">
        {FORMATS.map((fmt) => (
          <button
            key={fmt.key}
            className="export-btn"
            onClick={() => handleExport(fmt.key)}
            disabled={loading !== null}
            id={`export-${fmt.key}-btn`}
          >
            <span>{fmt.icon}</span>
            <span>Export as</span>
            <span className="format-badge" style={{ color: fmt.color, background: `${fmt.color}22` }}>
              {fmt.label}
            </span>
            {loading === fmt.key && (
              <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }}></span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
