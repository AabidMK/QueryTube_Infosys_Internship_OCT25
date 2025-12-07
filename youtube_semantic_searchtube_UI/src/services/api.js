import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health & Status
export const getHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getSummarizerStatus = async () => {
  const response = await api.get('/summarizer/status');
  return response.data;
};

// Search
// In src/services/api.js, make sure you have:
export const searchVideos = async (query, n_results = 10, filter_channel = null) => {
  try {
    const response = await api.post('/search/', {
      query,
      n_results,
      filter_channel
    });
    return response.data;
  } catch (error) {
    console.error('Search failed:', error);
    throw error;
  }
};

export const searchVideosWithSummary = async (query, n_results = 10, include_summary = true) => {
  const response = await api.post('/search/with_summary/', {
    query,
    n_results
  }, {
    params: { include_summary }
  });
  return response.data;
};

// Videos
export const getVideoById = async (video_id, include_summary = false) => {
  const response = await api.get(`/videos/${video_id}`, {
    params: { include_summary }
  });
  return response.data;
};

export const listVideos = async (limit = 20, offset = 0) => {
  const response = await api.get('/videos/', {
    params: { limit, offset }
  });
  return response.data;
};

// Summarization
export const summarizeVideo = async (video_id, use_ai = true, save_to_file = false) => {
  const response = await api.post('/summarize/', {
    video_id,
    use_ai,
    save_to_file
  });
  return response.data;
};

export const summarizeBatch = async (video_ids, use_ai = true, save_to_file = false) => {
  const response = await api.post('/summarize/batch/', {
    video_ids,
    use_ai,
    save_to_file
  });
  return response.data;
};

// Statistics
export const getStats = async () => {
  const response = await api.get('/stats/');
  return response.data;
};

export const testVideos = async () => {
  const response = await api.get('/test/videos');
  return response.data;
};

// Test Summary
export const testSummary = async (video_id, use_ai = true) => {
  const response = await api.get(`/test/summary/${video_id}`, {
    params: { use_ai }
  });
  return response.data;
};

export default api;