import { useState } from 'react';

export default function ErrorMessage({ error, onDismiss }) {
  if (!error) return null;

  return (
    <div className="error-banner animate-slideDown" role="alert">
      <span className="error-icon"></span>
      <span className="error-text">{error}</span>
      {onDismiss && (
        <button className="error-dismiss" onClick={onDismiss} aria-label="Dismiss error">
          ✕
        </button>
      )}
    </div>
  );
}
