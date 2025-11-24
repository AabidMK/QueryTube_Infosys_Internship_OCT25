import React, { useState } from "react";
import axios from "axios";
import { API_BASE } from "../api";

export default function ResultsPage(){
  const [query, setQuery] = useState("");
  const [k, setK] = useState(6);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return alert("Enter a search query.");
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/search`, { params: { query, k } , timeout: 60000});
      setResults(res.data);
    } catch (err) {
      console.error(err);
      alert("Search failed: " + (err?.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h2>Search Videos</h2>

        <div style={{display:"flex", gap:12, alignItems:"center", marginTop:8}}>
          <input
            className="input"
            placeholder="Ask something... e.g. 'how to tie a tie'"
            value={query}
            onChange={(e)=> setQuery(e.target.value)}
            style={{flex:1}}
          />
          <input
            type="number"
            min={1}
            max={20}
            value={k}
            onChange={(e)=> setK(Math.max(1, Math.min(20, Number(e.target.value))))}
            style={{width:72, padding:8, borderRadius:8}}
          />
          <button className="btn" onClick={handleSearch} disabled={loading}>{loading ? "Searching..." : "Search"}</button>
        </div>

        <div style={{marginTop:16}}>
          <small className="small">Tip: increase K to see more results.</small>
        </div>
      </div>

      {results && (
        <div style={{marginTop:18}}>
          <div className="card">
            <h3>Results for: <em>{results.query}</em></h3>
            <div className="results-grid" style={{marginTop:12}}>
              {Array.isArray(results.results) && results.results.length>0 ? results.results.map(item => (
                <div key={item.rank} className="card video-card" style={{flexDirection:"column", alignItems:"stretch"}}>
                  <div style={{display:"flex", gap:12}}>
                    <img className="video-thumb" src={item.thumbnail || `https://img.youtube.com/vi/${item.video_id}/hqdefault.jpg`} alt="thumb" />
                    <div style={{flex:1}}>
                      <h4 style={{margin:"0 0 6px 0"}}>{item.rank}. {item.title}</h4>
                      <div className="meta"><strong>{item.channel}</strong></div>
                      <div className="small">Views: {Number(item.views).toLocaleString()} • Likes: {Number(item.likes).toLocaleString()}</div>
                      <div style={{marginTop:8}} className="small"><strong>Summary:</strong> {item.summary}</div>
                      <div style={{marginTop:10}}>
                        <a className="watch-btn" href={item.video_url} target="_blank" rel="noreferrer">Watch on YouTube</a>
                        <span style={{marginLeft:12, color:"rgba(255,255,255,0.75)"}}>Score: {Number(item.similarity_score).toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )) : <div>No results returned.</div>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
