const API_BASE = 'http://localhost:8000/api';

/**
 * Generic fetch wrapper with error handling.
 */
async function request(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || `Request failed with status ${response.status}`;
      throw new Error(message);
    }

    // For file downloads, return the blob
    const contentType = response.headers.get('content-type') || '';
    if (
      contentType.includes('application/pdf') ||
      contentType.includes('text/csv') ||
      contentType.includes('application/xml') ||
      contentType.includes('text/markdown') ||
      options.responseType === 'blob'
    ) {
      return response.blob();
    }

    return response.json();
  } catch (error) {
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error('Unable to connect to the server. Please make sure the backend is running.');
    }
    throw error;
  }
}

// --- Weather API ---
export const weatherApi = {
  getCurrent: (location) =>
    request(`${API_BASE}/weather/current?location=${encodeURIComponent(location)}`),

  getForecast: (location) =>
    request(`${API_BASE}/weather/forecast?location=${encodeURIComponent(location)}`),

  geocode: (location) =>
    request(`${API_BASE}/weather/geocode?location=${encodeURIComponent(location)}`),
};

// --- CRUD Searches API ---
export const searchesApi = {
  create: (data) =>
    request(`${API_BASE}/searches`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  list: (skip = 0, limit = 50) =>
    request(`${API_BASE}/searches?skip=${skip}&limit=${limit}`),

  get: (id) =>
    request(`${API_BASE}/searches/${id}`),

  update: (id, data) =>
    request(`${API_BASE}/searches/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id) =>
    request(`${API_BASE}/searches/${id}`, {
      method: 'DELETE',
    }),
};

// --- Integrations API ---
export const integrationsApi = {
  getYouTubeVideos: (location, maxResults = 6) =>
    request(
      `${API_BASE}/integrations/youtube?location=${encodeURIComponent(location)}&max_results=${maxResults}`
    ),

  getMapsEmbedUrl: (location, lat, lon) => {
    let url = `${API_BASE}/integrations/maps-embed-url?location=${encodeURIComponent(location)}`;
    if (lat != null && lon != null) {
      url += `&lat=${lat}&lon=${lon}`;
    }
    return request(url);
  },
};

// --- Export API ---
export const exportApi = {
  downloadFile: async (format) => {
    const blob = await request(`${API_BASE}/export/${format}`, {
      responseType: 'blob',
    });
    
    const extensions = {
      json: 'json',
      csv: 'csv',
      xml: 'xml',
      markdown: 'md',
      pdf: 'pdf',
    };
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weather_searches.${extensions[format] || format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};
