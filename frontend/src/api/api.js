// src/api/api.js

// Use Vite environment variables safely
const API_BASE =
  import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";  
// Replace 8000 with whichever port your FastAPI is running on

async function jsonOrThrow(res) {
  const text = await res.text();
  try {
    const data = text ? JSON.parse(text) : {};
    if (!res.ok) {
      const err = new Error(data.detail || data.error || res.statusText || "Request failed");
      err.status = res.status;
      err.body = data;
      throw err;
    }
    return data;
  } catch (e) {
    if (!res.ok) {
      const err = new Error(res.statusText || "Request failed");
      err.status = res.status;
      throw err;
    }
    return JSON.parse(text || "{}");
  }
}

export async function apiGet(path) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url);
  return jsonOrThrow(res);
}

export async function apiPost(path, body) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return jsonOrThrow(res);
}

export { API_BASE };
