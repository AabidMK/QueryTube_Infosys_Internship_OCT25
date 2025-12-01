import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export const uploadCsv = (file) => {
  const fd = new FormData();
  fd.append("file", file);
  return apiClient.post("/upload_csv", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const fetchVideoDetails = (id) => apiClient.get(`/videos/${id}`);
export const searchVideos = (query) => apiClient.post("/search", { query });
export const generateSummary = (id) =>
  apiClient.post("/generate_summary", { video_id: id });