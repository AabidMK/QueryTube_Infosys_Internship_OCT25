import React, { useState, useEffect } from "react";

// Browser-safe API base lookup
const API_BASE = (() => {
  if (typeof window !== "undefined") {
    if (window.__REACT_APP_API_BASE_URL__) return window.__REACT_APP_API_BASE_URL__;
    if (window.REACT_APP_API_BASE_URL) return window.REACT_APP_API_BASE_URL;
  }
  if (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE) return import.meta.env.VITE_API_BASE;
  return "http://127.0.0.1:8000";
})();

export default function ChromaIngestUI() {
  const [videoId, setVideoId] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatus();
    // eslint-disable-next-line
  }, []);

  async function fetchStatus() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/status`);
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      setError(`Could not reach API: ${err.message}`);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest(e) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    if (!videoId.trim() || !title.trim() || !content.trim()) {
      setError("Please fill all fields before ingesting.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: videoId, title, content }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Status ${res.status}`);
      }
      const data = await res.json();
      setMessage(`Ingested ✓ — video_id: ${data.video_id}`);
      setVideoId("");
      setTitle("");
      setContent("");
      await fetchStatus();
    } catch (err) {
      setError(`Ingestion failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    if (!window.confirm("This will delete the 'video_transcripts' collection. Continue?")) return;
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reset_db`, { method: "POST" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Status ${res.status}`);
      }
      const data = await res.json();
      setMessage(data.message || "Collection reset.");
      await fetchStatus();
    } catch (err) {
      setError(`Reset failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm">
      <h2 className="text-2xl font-semibold mb-3">Ingest — Add transcript</h2>
      <form onSubmit={handleIngest}>
        <label className="block mb-1 text-sm">Video ID</label>
        <input value={videoId} onChange={(e) => setVideoId(e.target.value)} className="w-full p-2 mb-3 rounded border" placeholder="vid_123" />

        <label className="block mb-1 text-sm">Title</label>
        <input value={title} onChange={(e) => setTitle(e.target.value)} className="w-full p-2 mb-3 rounded border" placeholder="Video title" />

        <label className="block mb-1 text-sm">Transcript</label>
        <textarea value={content} onChange={(e) => setContent(e.target.value)} className="w-full p-3 mb-3 rounded border h-36" />

        <div className="flex gap-3">
          <button className="px-4 py-2 bg-indigo-600 text-white rounded" disabled={loading}>{loading ? "Working..." : "Ingest Document"}</button>
          <button type="button" onClick={handleReset} className="px-3 py-2 bg-rose-500 text-white rounded">Reset Collection</button>
          <button type="button" onClick={fetchStatus} className="ml-auto px-3 py-2 border rounded">Refresh Status</button>
        </div>

        {message && <div className="mt-3 p-2 bg-emerald-50 border text-emerald-700">{message}</div>}
        {error && <div className="mt-3 p-2 bg-rose-50 border text-rose-700">{error}</div>}

        <div className="mt-4 text-sm text-slate-500">API Base: {API_BASE}</div>
      </form>
    </div>
  );
}
