// src/pages/Summarize.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiGet } from "../api/api";

export default function Summarize() {
  const { videoId } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!videoId) return;
    setLoading(true);
    apiGet(`/summarize/${encodeURIComponent(videoId)}`)
      .then(d => setSummary(d.summary || "No summary available."))
      .catch(e => setSummary("Error fetching summary"))
      .finally(() => setLoading(false));
  }, [videoId]);

  const openYouTube = (id) => window.open(`https://www.youtube.com/watch?v=${id}`, "_blank", "noopener");

  return (
    <div className="pt-28 max-w-3xl mx-auto px-6">
      <div className="glass-card p-6 rounded-2xl">
        <h1 className="text-2xl font-bold mb-4">Summary</h1>
        <div className="prose text-gray-900 whitespace-pre-wrap">
          {loading ? "Loading..." : summary}
        </div>
        <div className="mt-4 flex gap-3">
          <Link to="/search" className="text-sm text-purple-700 underline">Back to Search</Link>
          <button onClick={() => openYouTube(videoId)} className="px-3 py-2 rounded-lg bg-white/10 text-white">Open on YouTube</button>
        </div>
      </div>
    </div>
  );
}
