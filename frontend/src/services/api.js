import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 Making ${config.method?.toUpperCase()} request to: ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ Received response from: ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Response error:', error);
    return Promise.reject(error);
  }
);

export const searchAPI = {
  search: async (query, top_k = 5) => {
    try {
      const response = await api.post('/search', { query, top_k });
      return response.data;
    } catch (error) {
      console.error('Search API error:', error);
      throw error;
    }
  },
};

export const uploadAPI = {
  ingest: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Upload API error:', error);
      throw error;
    }
  },
};

export const summaryAPI = {
  getSummary: async (videoId) => {
    try {
      const response = await api.get(`/summary/${videoId}`);
      return response.data;
    } catch (error) {
      console.error('Summary API error:', error);
      throw error;
    }
  },
};

export const healthAPI = {
  check: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health API error:', error);
      throw error;
    }
  },
  
  getInfo: async () => {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('API info error:', error);
      throw error;
    }
  },
};

export default api;