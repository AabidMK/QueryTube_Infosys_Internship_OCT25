import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../api";

export default function UploadPage(){
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return alert("Please choose a CSV file to upload.");

    const form = new FormData();
    form.append("file", file);

    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE}/ingest`, form, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000
      });
      alert("Upload succeeded: " + (res.data?.records ?? "records ingested"));
      // go to results page
      navigate("/results");
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err?.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h2>Upload CSV</h2>
        <p className="small">CSV should include at least these columns: <code>video_id, title, channel_title, text_embedding</code>. Optional: transcript, description, thumbnail, video_url, views, likes.</p>

        <div className="upload-area" style={{marginTop:12}}>
          <input type="file" accept=".csv" onChange={(e)=> setFile(e.target.files?.[0]||null)} />
          <button className="btn" onClick={handleUpload} disabled={loading}>
            {loading ? "Uploading..." : "Upload & Build Index"}
          </button>
        </div>

        <div style={{marginTop:16}} className="small">
          Tip: text_embedding column must contain a JSON array representation of the vector, e.g. "[0.1,0.2,...]". Parser will try to handle common variants.
        </div>
      </div>
    </div>
  );
}
