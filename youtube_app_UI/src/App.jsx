"use client";

import { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState("");
  const [videoId, setVideoId] = useState("");
  const [results, setResults] = useState([]);
  const [videoData, setVideoData] = useState(null);
  const [summary, setSummary] = useState("");
  const [status, setStatus] = useState("");
  const [activeTab, setActiveTab] = useState("upload");

  const handleUpload = async () => {
    if (!file) return setStatus("Select a CSV first");
    setStatus("Uploading...");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API_URL}/upload_csv`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus(`✅ Success`);
    } catch (e) {
      setStatus(`❌ Error: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleSearch = async () => {
    if (!query) return setStatus("Enter a query");
    setStatus("Searching...");
    try {
      const res = await axios.post(`${API_URL}/search`, { query });
      setResults(res.data.results);
      setStatus(`Found ${res.data.results.length} results`);
    } catch (e) {
      setStatus(`❌ Error: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleGetById = async () => {
    if (!videoId) return setStatus("Enter video ID");
    setStatus("Fetching video...");
    try {
      const res = await axios.get(`${API_URL}/videos/${videoId}`);
      setVideoData(res.data);
      setSummary("");
      setStatus("Video fetched successfully");
    } catch (e) {
      setVideoData(null);
      setStatus(`❌ Error: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleGenerateSummary = async () => {
    if (!videoId) return setStatus("Enter video ID for summary");
    setStatus("Generating summary...");
    try {
      const res = await axios.get(`${API_URL}/generate_summary/${videoId}`);
      setSummary(res.data.summary);
      setStatus("Summary generated");
    } catch (e) {
      setSummary("");
      setStatus(`❌ Error: ${e.response?.data?.detail || e.message}`);
    }
  };

  // --- Styles ---
  const tabStyle = (tab) => ({
    padding: "0.5rem 1rem",
    marginRight: "1rem",
    cursor: "pointer",
    borderRadius: "5px",
    backgroundColor: activeTab === tab ? "#4A70A9" : "#8FABD4",
    color: activeTab === tab ? "#EFECE3" : "#000000",
    fontWeight: activeTab === tab ? "600" : "400",
    transition: "background-color 0.3s",
  });

  const cardStyle = {
    border: "1px solid #4A70A9",
    borderRadius: "8px",
    padding: "1rem",
    margin: "1rem 0",
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
    backgroundColor: "#EFECE3",
    color: "#000000",
  };

  const buttonStyle = (color = "#4A70A9") => ({
    padding: "0.5rem 1rem",
    backgroundColor: color,
    color: "#EFECE3",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    fontWeight: "bold",
    transition: "background-color 0.3s",
  });

  const sectionStyle = {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
    alignItems: "center",
    // Added maxWidth to keep content readable while centering
    maxWidth: "900px", 
    width: "100%",
  };

  const inputStyle = {
    padding: "0.5rem",
    borderRadius: "5px",
    border: "1px solid #4A70A9",
    width: "100%",
    maxWidth: "500px",
    color: "#000000",
  };

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "Arial, sans-serif",
        // maxWidth: "900px", // REMOVED: To occupy full width
        margin: "0", // CHANGED: To occupy full width
        color: "#000000",
        // textAlign: "center", // REMOVED: Replaced by flexbox for better centering
        
        // ADDED: Flexbox properties for full screen & center alignment
        display: "flex", 
        flexDirection: "column",
        alignItems: "center", // Center content horizontally
        // END OF ADDED FLEXBOX
        
        backgroundColor: "#EFECE3",
        minHeight: "100vh",
        width: "100vw", // ADDED: Occupy full screen width
      }}
    >
      <h1 style={{ color: "#4A70A9", marginBottom: "2rem" }}>
        🎥 YouTube VectorDB Dashboard 💾
      </h1>

      <div
        style={{
          marginBottom: "2rem",
          display: "inline-flex",
          justifyContent: "center",
        }}
      >
        <span style={tabStyle("upload")} onClick={() => setActiveTab("upload")}>
          Upload CSV
        </span>
        <span style={tabStyle("search")} onClick={() => setActiveTab("search")}>
          Search
        </span>
        <span style={tabStyle("video")} onClick={() => setActiveTab("video")}>
          Video / Summary
        </span>
      </div>

      {status && (
        <p style={{ color: "#4A70A9", fontWeight: "700", marginBottom: "1.5rem" }}>
          {status}
        </p>
      )}

      {/* Upload Tab */}
      {activeTab === "upload" && (
        <div style={sectionStyle}>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            style={{
              width: "100%",
              maxWidth: "500px",
              margin: "0.5rem 0",
            }}
          />
          <button onClick={handleUpload} style={buttonStyle("#4A70A9")}>
            Upload CSV to DB
          </button>
        </div>
      )}

      {/* Search Tab */}
      {activeTab === "search" && (
        // REMOVED alignItems: "stretch" to respect sectionStyle's centering
        <div style={sectionStyle}> 
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1rem",
              width: "100%",
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              style={inputStyle}
            />
            <button onClick={handleSearch} style={buttonStyle("#4A70A9")}>
              Search Database
            </button>
          </div>

          <div style={{ marginTop: "1rem", width: "100%", textAlign: "left" }}>
            {results.map((r) => (
              <div key={r.video_id} style={cardStyle}>
                <a
                  href={r.youtube_url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ display: "block", marginBottom: "0.5rem" }}
                >
                  <img
                    src={r.thumbnail}
                    alt={r.title}
                    width={320}
                    style={{ borderRadius: "5px", display: "block" }}
                  />
                </a>

                <h3 style={{ color: "#4A70A9", margin: "0.5rem 0" }}>
                  {r.title}
                </h3>

                <p>
                  <strong>{r.channel_title}</strong> | Views: {r.view_count} |
                  Duration: {r.duration}
                </p>

                {/* FIXED — Now showing correct transcript snippet */}
                <p style={{ fontStyle: "italic", margin: "0.5rem 0" }}>
                  Snippet: {r.transcript_snippet}
                </p>

                <p style={{ fontWeight: "bold" }}>
                  Relevance Score: {r.score.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video / Summary Tab */}
      {activeTab === "video" && (
        <div style={sectionStyle}>
          <input
            type="text"
            value={videoId}
            onChange={(e) => setVideoId(e.target.value)}
            placeholder="Enter YouTube Video ID"
            style={inputStyle}
          />
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button onClick={handleGetById} style={buttonStyle("#4A70A9")}>
              Fetch Video Details
            </button>
            <button onClick={handleGenerateSummary} style={buttonStyle("#4A70A9")}>
              Generate Summary
            </button>
          </div>

          {videoData && (
            <div
              style={{
                ...cardStyle,
                textAlign: "left",
                width: "100%",
                maxWidth: "500px",
              }}
            >
              <h2 style={{ color: "#4A70A9", margin: "0 0 0.5rem 0" }}>
                {videoData.title}
              </h2>

              <p style={{ marginBottom: "1rem" }}>
                <strong>{videoData.channel_title}</strong> | Views:
                {videoData.view_count} | Duration: {videoData.duration}
              </p>

              <div style={{ textAlign: "center", marginBottom: "1rem" }}>
                <a href={videoData.youtube_url} target="_blank" rel="noreferrer">
                  <img
                    src={videoData.thumbnail}
                    alt={videoData.title}
                    width={320}
                    style={{ borderRadius: "5px" }}
                  />
                </a>
              </div>

              <p>
                <strong>Video ID:</strong> {videoData.video_id}
              </p>

              <p>
                <strong>Transcript Snippet:</strong>{" "}
                {videoData.transcript.slice(0, 500)}...
              </p>

              {summary && (
                <p
                  style={{
                    marginTop: "1rem",
                    backgroundColor: "#8FABD4",
                    padding: "0.75rem",
                    borderRadius: "5px",
                    color: "#000000",
                  }}
                >
                  <strong>Summary:</strong>{" "}
                  <span style={{ fontWeight: "normal" }}>{summary}</span>
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}