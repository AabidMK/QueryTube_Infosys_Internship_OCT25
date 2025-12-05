import React, { useState } from "react";

const API_BASE = (() => {
  if (typeof window !== "undefined") {
    if (window.__REACT_APP_API_BASE_URL__) return window.__REACT_APP_API_BASE_URL__;
    if (window.REACT_APP_API_BASE_URL) return window.REACT_APP_API_BASE_URL;
  }
  if (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE) return import.meta.env.VITE_API_BASE;
  return "http://127.0.0.1:8000";
})();

export default function ChromaQueryUI() {
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);
  const [summaries, setSummaries] = useState({}); // id -> summary

  async function handleSearch(e) {
    e && e.preventDefault();
    setLoading(true);
    setError(null);
    setResults([]);
    if (!query.trim()) {
      setError("Please enter a search query.");
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), top_k: Number(topK) }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Status ${res.status}`);
      }
      const data = await res.json();
      setResults(Array.isArray(data.results) ? data.results : []);
    } catch (err) {
      setError(`Query failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function fetchSummary(id) {
    setSummaries(prev => ({ ...prev, [id]: "Loading..." }));
    try {
      const res = await fetch(`${API_BASE}/summarize/${encodeURIComponent(id)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Status ${res.status}`);
      }
      const data = await res.json();
      setSummaries(prev => ({ ...prev, [id]: data.summary }));
    } catch (err) {
      setSummaries(prev => ({ ...prev, [id]: `Error: ${err.message}` }));
    }
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm">
      <h2 className="text-2xl font-semibold mb-3">Query — Semantic Search</h2>

      <form onSubmit={handleSearch}>
        <input value={query} onChange={(e) => setQuery(e.target.value)} className="w-full p-2 rounded border mb-3" placeholder="Ask something about your videos..." />
        <div className="flex items-center gap-3 mb-3">
          <label className="text-sm">Top K</label>
          <input type="number" min={1} max={50} value={topK} onChange={(e) => setTopK(e.target.value)} className="w-24 p-2 rounded border" />
          <button className="ml-auto px-4 py-2 bg-indigo-600 text-white rounded" disabled={loading}>{loading ? "Searching..." : "Search"}</button>
        </div>
      </form>

      {error && <div className="text-rose-700 mb-3">{error}</div>}

      <div className="space-y-4">
        {results.length === 0 && <div className="text-sm text-slate-500">No results yet.</div>}

        {results.map((r, idx) => (
          <article key={r.id || idx} className="p-4 bg-slate-50 rounded">
            <div className="flex justify-between mb-2">
              <div>
                <div className="text-sm text-slate-600">{r.metadata?.title || r.metadata?.video_id || r.id}</div>
                <div className="text-xs text-slate-400">id: {r.id}</div>
              </div>
              <div className="text-sm font-medium">Score: {Number(r.score).toFixed(4)}</div>
            </div>

            <div className="text-sm text-slate-700 whitespace-pre-wrap">{r.document || r.content || r.text}</div>

            <div className="mt-3 flex items-center gap-3">
              <button onClick={() => fetchSummary(r.id)} className="px-3 py-1 rounded bg-amber-500 text-white">Summarize</button>
              {summaries[r.id] && (
                <div className="ml-3 text-sm text-slate-600 whitespace-pre-wrap">{summaries[r.id]}</div>
              )}
            </div>

            {r.metadata && <div className="mt-3 text-xs text-slate-400">Metadata: {JSON.stringify(r.metadata)}</div>}
          </article>
        ))}
      </div>

      <div className="mt-4 text-sm text-slate-500">API Base: {API_BASE}</div>
    </div>
  );
}
