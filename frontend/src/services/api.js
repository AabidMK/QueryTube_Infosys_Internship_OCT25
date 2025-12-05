// src/services/api.js
import axios from "axios";
import { API_URL } from "../config";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export default api;

// helper wrapper for search (optional named export)
export const searchAPI = {
  // call GET /search?query=...
  async search(query) {
    const res = await api.get("/search", { params: { query } });
    // backend returns { query, results } — adapt as needed
    return res.data;
  },
  // call GET /summarize/:videoId
  async summarize(videoId) {
    const res = await api.get(`/summarize/${videoId}`);
    return res.data;
  }
};
