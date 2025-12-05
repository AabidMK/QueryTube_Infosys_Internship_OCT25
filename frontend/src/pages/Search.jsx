// Search.jsx — REPLACEMENT for Ingestion functionality

import { useState } from "react";
import { apiPost, API_BASE } from "../api/api";
import { useNavigate } from "react-router-dom";

/*
  Behavior:
   - Only shows CSV upload functionality (now titled Ingest Video Data).
   - Upon successful upload, redirects to the Home page (path '/') for quick search.
*/

export default function Search() {
  const navigate = useNavigate();

  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  // upload CSV and redirect to Home on success
  async function handleCsvUpload(file) {
    if (!file) return;
    setUploading(true);
    setUploadMessage("Uploading CSV…");
    try {
      const form = new FormData();
      form.append("file", file);

      const raw = await fetch(`${API_BASE}/upload-csv`, { method: "POST", body: form });
      const data = await raw.json();

      if (!raw.ok) {
        setUploadMessage(data.error || "Upload failed");
        setUploading(false);
        return;
      }

      // Success: Display message and redirect to the Home page (for Quick Search)
      setUploadMessage(`✅ Uploaded ${data.count || 0} items. Redirecting to Search...`);
      setTimeout(() => navigate('/'), 1000); // Redirect to Home

    } catch (err) {
      console.error("CSV upload error:", err);
      setUploadMessage("❌ CSV upload failed");
    } finally {
      // In case of a failure, stop loading and clear message after delay
      if (!uploadMessage.includes('Redirecting')) {
        setUploading(false);
        setTimeout(() => setUploadMessage(""), 5000);
      }
    }
  }

  // UI render
  return (
    <div className="pt-24 max-w-6xl mx-auto px-6">
  <div style={{ paddingTop: 88 }}>
      <div className="glass-card p-6 rounded-xl mb-6">
  
        <h2 className="text-2xl font-semibold mb-3">Ingest Video Data (CSV Upload)</h2>
        
        
        <input 
          type="file" 
          accept=".csv" 
          onChange={(e) => handleCsvUpload(e.target.files?.[0])} 
          disabled={uploading} 
        />
        
        {uploadMessage && (
          <div className={`mt-4 text-sm font-medium ${uploadMessage.includes('failed') || uploadMessage.includes('❌') ? 'text-red-600' : 'text-green-600'}`}>
            {uploadMessage}
          </div>
        )}

        {/* Button to redirect to home for quick search */}
        <button 
          className="btn-accent mt-6" 
          onClick={() => navigate('/')}
          disabled={uploading}
        >
          Go to Quick Search
        </button>
</div>
      </div>
    </div>
  );
}