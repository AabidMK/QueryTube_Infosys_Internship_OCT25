import React, { useState } from "react";
import * as api from "./api";
import "./App.css";

// Extract YouTube ID helper (robust)
// Replace your existing extractId function at the top of app.jsx
const extractId = (urlOrId) => {
  if (!urlOrId) return "";
  
  // CRITICAL FIX: Trim whitespace
  const cleanStr = urlOrId.toString().trim();

  // Match standard YouTube URL patterns
  const match =
    cleanStr.match(/(?:v=|\/)([0-9A-Za-z_-]{11})/) ||
    cleanStr.match(/youtu\.be\/([0-9A-Za-z_-]{11})/);
    
  // If match found, return ID. If not, return the cleaned string (assuming it is the ID)
  return match ? match[1] : cleanStr;
};

// CSV Upload
function CsvUploadComponent() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return setStatus("Select a CSV first");
    setLoading(true);
    setStatus("Uploading...");
    try {
      const res = await api.uploadCsv(file);
      // Implemented Modification 1: Show simple success message with details
      const { rows_added, total_in_collection } = res.data;
      setStatus(`CSV uploaded successfully!.`);
    } catch (err) {
      setStatus(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Upload CSV</h2>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading…" : "Upload"}
      </button>
      {status && <p className={status.includes('successfully') ? '' : 'error'}>{status}</p>}
      <small>
        CSV columns allowed: video_id, transcript, description, title,
        channel_title, view_count, duration
      </small>
    </div>
  );
}

// Fetch Details
function FetchDetailsComponent() {
  const [videoId, setVideoId] = useState("");
  const [video, setVideo] = useState(null);
  const [err, setErr] = useState("");

  const fetchDetails = async () => {
    if (!videoId) return setErr("Enter video ID or URL");
    setErr("");
    setVideo(null);
    try {
      const res = await api.fetchVideoDetails(extractId(videoId));
      setVideo(res.data);
    } catch (e) {
      setErr(e.response?.data?.detail || e.message);
    }
  };

  return (
    <div className="card">
      <h2>Fetch Video Details</h2>
      <div className="input-group">
        <input
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
          placeholder="Video ID or URL (e.g., dQw4w9WgXcQ)"
        />
        <button onClick={fetchDetails}>Fetch</button>
      </div>
      {err && <p className="error">{err}</p>}
      {video && (
        <div className="video-box">
          <img
            src={`https://img.youtube.com/vi/${extractId(
              video.video_id
            )}/hqdefault.jpg`}
            alt="thumb"
            className="thumbnail"
          />
          <h3>{video.title}</h3>
          <p>
            <strong>Channel:</strong> {video.channel_title}
          </p>
          <p>
            <strong>Views:</strong> {video.view_count}
          </p>
          <p>
            <strong>Duration:</strong> {video.duration}
          </p>
          <h4>Transcript preview</h4>
          <pre>
            {(video.transcript || "").slice(0, 600)}
            {(video.transcript || "").length > 600 ? "..." : ""}
          </pre>
          <a href={video.youtube_url} target="_blank" rel="noreferrer">
            Open on YouTube
          </a>
        </div>
      )}
    </div>
  );
}

// Generate summary
// Semantic search
function SemanticSearchComponent() {
  const [query, setQuery] = useState("");
  // Default to 5 results to match backend
  const [k, setK] = useState(5); 
  const [results, setResults] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const doSearch = async () => {
    if (!query.trim()) return setMsg("⚠️ Enter a valid query");
    
    setMsg("Searching...");
    setLoading(true);
    setResults([]);

    try {
      // Using your existing api.js
      const res = await api.searchVideos(query);
      const r = res.data.results;

      if (!r || r.length === 0) {
        setMsg("No results found");
      } else {
        setResults(r);
        setMsg(`Found ${r.length} relevant results.`);
      }
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🔍 Search Videos</h2>

      {/* Input Section */}
      <div className="input-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query..."
        />
        {/* Optional: Input for K (Number of results) */}
        <input 
          type="number" 
          min="1" 
          max="10" 
          value={k} 
          onChange={(e) => setK(e.target.value)}
          style={{ maxWidth: '80px' }} 
        />
        <button onClick={doSearch} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {msg && <p className={msg.includes("Found") ? "" : "error"}>{msg}</p>}

      {/* Results Loop */}
      {results.map((r) => (
        <div key={r.video_id} className="result-card">
          
          {/* THE VIDEO PLAYER */}
          <div className="video-embed-in-card">
            <iframe
              src={`https://www.youtube.com/embed/${extractId(r.video_id)}`}
              title={r.title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>

          {/* Metadata & Text */}
          <div className="result-content">
            <h4>{r.title}</h4>
            
            <div className="metadata">
              <p>Channel: <strong>{r.channel_title || "N/A"}</strong></p>
              <p>Score: <strong>{Number(r.score).toFixed(4)}</strong></p>
            </div>

            <p className="snippet">{r.snippet}</p>
            
            <a href={r.youtube_url} target="_blank" rel="noreferrer">
              Watch on YouTube ↗
            </a>
          </div>
        </div>
      ))}
    </div>
  );
}

// Semantic search
// Semantic search
// Replace your existing SemanticSearchComponent

// Main App
export default function App() {
  const [tab, setTab] = useState("upload");

  return (
    <div className="app-container">
      <h1 className="title">YouTube Vector DB + Semantic Dashboard</h1>

      <div className="tabs">
        <button
          className={tab === "upload" ? "active" : ""}
          onClick={() => setTab("upload")}
        >
          Upload CSV
        </button>
        <button
          className={tab === "fetch" ? "active" : ""}
          onClick={() => setTab("fetch")}
        >
          Fetch Details
        </button>
        <button
          className={tab === "search" ? "active" : ""}
          onClick={() => setTab("search")}
        >
          Semantic Search
        </button>
        <button
          className={tab === "summary" ? "active" : ""}
          onClick={() => setTab("summary")}
        >
          Generate Summary
        </button>
      </div>

      <div className="content-area">
        {tab === "upload" && <CsvUploadComponent />}
        {tab === "fetch" && <FetchDetailsComponent />}
        {tab === "search" && <SemanticSearchComponent />}
        {tab === "summary" && <GenerateSummaryComponent />}
      </div>
    </div>
  );
}