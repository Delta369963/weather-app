import { useState, useEffect, useCallback } from 'react';
import { searchesApi } from '../api';
import ErrorMessage from './ErrorMessage';

export default function SearchHistory({ refreshTrigger }) {
  const [searches, setSearches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({ location: '', date_from: '', date_to: '' });
  const [deletingId, setDeletingId] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchSearches = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchesApi.list();
      setSearches(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSearches();
  }, [fetchSearches, refreshTrigger]);

  // --- Edit ---
  const startEdit = (search) => {
    setEditingId(search.id);
    setEditForm({
      location: search.location,
      date_from: search.date_from?.split('T')[0] || '',
      date_to: search.date_to?.split('T')[0] || '',
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({ location: '', date_from: '', date_to: '' });
  };

  const saveEdit = async () => {
    if (!editForm.location.trim()) return;
    setActionLoading(true);
    setError(null);
    try {
      const payload = {};
      if (editForm.location) payload.location = editForm.location;
      if (editForm.date_from) payload.date_from = editForm.date_from;
      if (editForm.date_to) payload.date_to = editForm.date_to;

      await searchesApi.update(editingId, payload);
      cancelEdit();
      fetchSearches();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  // --- Delete ---
  const confirmDelete = async () => {
    setActionLoading(true);
    setError(null);
    try {
      await searchesApi.delete(deletingId);
      setDeletingId(null);
      fetchSearches();
    } catch (err) {
      setError(err.message);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="glass-card animate-fadeIn">
      <div className="card-title" style={{ justifyContent: 'space-between' }}>
        <span>
          <span className="icon"></span> Search History
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginLeft: '0.5rem' }}>
            ({searches.length} records)
          </span>
        </span>
        <button className="btn btn-secondary btn-sm" onClick={fetchSearches} disabled={loading}>
          Refresh
        </button>
      </div>

      <ErrorMessage error={error} onDismiss={() => setError(null)} />

      {loading ? (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      ) : searches.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"></div>
          <div className="empty-title">No searches saved yet</div>
          <div className="empty-desc">
            Search for weather and save it using the "Save to Database" section to see records here.
          </div>
        </div>
      ) : (
        <div className="history-table-wrapper">
          <table className="history-table" id="search-history-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Temp</th>
                <th>Weather</th>
                <th>Humidity</th>
                <th>Wind</th>
                <th>Date From</th>
                <th>Date To</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {searches.map((search) => {
                const weather = search.weather_data || {};
                return (
                  <tr key={search.id}>
                    <td style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
                      {search.location}
                    </td>
                    <td>{weather.temperature != null ? `${Math.round(weather.temperature)}°C` : 'N/A'}</td>
                    <td style={{ textTransform: 'capitalize' }}>{weather.description || 'N/A'}</td>
                    <td>{weather.humidity != null ? `${weather.humidity}%` : 'N/A'}</td>
                    <td>{weather.wind_speed != null ? `${weather.wind_speed} m/s` : 'N/A'}</td>
                    <td>{search.date_from?.split('T')[0] || 'N/A'}</td>
                    <td>{search.date_to?.split('T')[0] || 'N/A'}</td>
                    <td>{search.created_at ? new Date(search.created_at).toLocaleDateString() : 'N/A'}</td>
                    <td>
                      <div className="actions-cell">
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => startEdit(search)}
                          title="Edit"
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => setDeletingId(search.id)}
                          title="Delete"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Modal */}
      {editingId && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && cancelEdit()}>
          <div className="modal-content">
            <h2>Edit Search Record</h2>
            <div className="form-group">
              <label className="form-label">Location</label>
              <input
                className="form-input"
                type="text"
                value={editForm.location}
                onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                placeholder="City, zip code, or coordinates"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Date From</label>
              <input
                className="form-input"
                type="date"
                value={editForm.date_from}
                onChange={(e) => setEditForm({ ...editForm, date_from: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Date To</label>
              <input
                className="form-input"
                type="date"
                value={editForm.date_to}
                onChange={(e) => setEditForm({ ...editForm, date_to: e.target.value })}
              />
            </div>
            <ErrorMessage error={error} onDismiss={() => setError(null)} />
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={cancelEdit}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={saveEdit}
                disabled={actionLoading || !editForm.location.trim()}
              >
                {actionLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setDeletingId(null)}>
          <div className="modal-content confirm-dialog">
            <h2>Delete Record</h2>
            <p>Are you sure you want to delete this search record? This action cannot be undone.</p>
            <div className="confirm-actions">
              <button className="btn btn-secondary" onClick={() => setDeletingId(null)}>
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={confirmDelete}
                disabled={actionLoading}
              >
                {actionLoading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
