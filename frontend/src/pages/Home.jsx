// Home.jsx
import { useState } from "react";
import { apiPost, apiGet } from "../api/api";
import { useNavigate } from "react-router-dom";

const FALLBACK_IMG = "/assets/semantic.jpg"; // reliable public path

export default function Home() {
  const navigate = useNavigate();
  const [quickQuery, setQuickQuery] = useState("");
  const [results, setResults] = useState([]); // { r, metaLoading, meta, commentsLoading, comments, playing }
  const [loading, setLoading] = useState(false);

  async function doQuickSearch() {
    const q = (quickQuery || "").trim();
    if (!q) {
      navigate("/search");
      return;
    }
    setLoading(true);
    try {
      const res = await apiPost("/query", { query: q, top_k: 50 });
      const rows = (res.results || []).map(r => ({
        r,
        id: r.id || r.metadata?.video_id || null,
        metaLoading: false,
        metaError: null,
        meta: null,
        commentsLoading: false,
        commentsError: null,
        comments: [],
        playing: false
      }));
      setResults(rows);

      // fetch meta + comments for each result (non-blocking)
      rows.forEach(async (item, idx) => {
        const vid = item.id;
        if (!vid) return;

        // mark meta loading
        setResults(prev => prev.map((p, i) => i === idx ? { ...p, metaLoading: true, metaError: null } : p));

        try {
          const meta = await apiGet(`/youtube/meta/${vid}`);
          setResults(prev => prev.map((p, i) => i === idx ? { ...p, metaLoading: false, meta } : p));
        } catch (e) {
          setResults(prev => prev.map((p, i) => i === idx ? { ...p, metaLoading: false, metaError: e.message } : p));
        }

        // comments
        setResults(prev => prev.map((p, i) => i === idx ? { ...p, commentsLoading: true, commentsError: null } : p));
        try {
          const c = await apiGet(`/youtube/comments/${vid}`);
          setResults(prev => prev.map((p, i) => i === idx ? { ...p, commentsLoading: false, comments: (c.comments||[]) } : p));
        } catch (e) {
          setResults(prev => prev.map((p, i) => i === idx ? { ...p, commentsLoading: false, commentsError: e.message } : p));
        }
      });

    } catch (err) {
      console.error("Search failed", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  function pickThumb(id) {
    if (!id) return FALLBACK_IMG;
    return `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
  }

  return (
    <div style={{ paddingTop: 88 }}>
      <main style={{ maxWidth: 950, margin: "0 auto", padding: "20px" }}>
        <div className="glass-card" style={{ padding: 20, marginBottom: 18 }}>
          <h1 style={{ color: "#7c3aed" }}>QueryTube</h1>
          <p>Quick-search video transcripts with natural language.</p>
          <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
            <input
              value={quickQuery}
              onChange={(e) => setQuickQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && doQuickSearch()}
              placeholder="Try: how to evaluate model accuracy"
              style={{ padding: 10, borderRadius: 8, flex: 1 }}
            />
            <button onClick={doQuickSearch} className="btn-accent">{loading ? "Searching…" : "Quick search"}</button>
          </div>
        </div>

        <div style={{ display: "grid", gap: 12 }}>
          {results.length === 0 && !loading && <div style={{ color: "#777" }}>No results yet.</div>}
          {results.map((item, idx) => {
            const { r, id, metaLoading, meta, metaError, commentsLoading, comments, commentsError, playing } = item;
            const title = r.metadata?.title || meta?.title || "Untitled";
            const sim = r.score ?? r.similarity_score;

            return (
              <div key={idx} className="glass-card p-4" style={{ display: "flex", gap: 12 }}>
                <div style={{ width: 200 }}>
                  {!playing ? (
                    <div style={{ position: "relative", height: 120 }}>
                      <img src={pickThumb(id)} alt={title} style={{ width: "100%", height: "100%", objectFit: "cover" }} onError={(e) => e.currentTarget.src = FALLBACK_IMG} />
                      {id && <button className="btn-accent" style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)" }} onClick={() => setResults(prev => prev.map((p, i) => i === idx ? { ...p, playing: true } : p))}>▶ Play</button>}
                    </div>
                  ) : (
                    <div style={{ position: "relative", height: 120 }}>
                      <iframe title={`yt-${id}`} src={`https://www.youtube.com/embed/${id}?autoplay=1&rel=0`} style={{ width: "100%", height: "100%" }} allow="autoplay; encrypted-media" />
                      <button className="btn-accent" style={{ position: "absolute", right: 8, top: 8 }} onClick={() => setResults(prev => prev.map((p, i) => i === idx ? { ...p, playing: false } : p))}>Close</button>
                    </div>
                  )}
                </div>

                <div style={{ flex: 1 }}>
                  <h3>{title}</h3>

                  <div style={{ marginTop: 8 }}>
                    <div>Views: {metaLoading ? "Loading..." : (meta?.views ?? "Not available")}</div>
                    <div>Likes: {metaLoading ? "Loading..." : (meta?.likes ?? "Not available")}</div>
                    <div>Comments: {metaLoading ? "Loading..." : (meta?.commentCount ?? "Not available")}</div>
                    <div>Similarity Score: {sim !== undefined ? Number(sim).toFixed(4) : "—"}</div>
                  </div>

                  <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                    <button className="btn-accent" onClick={() => window.open(`https://www.youtube.com/watch?v=${id}`, "_blank")}>YouTube</button>
                    <button className="btn-accent" onClick={() => navigate(`/summarize/${id}`)}>Summarize</button>
                  </div>

                  <div style={{ marginTop: 12 }}>
                    <h4 style={{ marginBottom: 8 }}>Top comments</h4>
                    {commentsLoading && <div>Loading comments…</div>}
                    {commentsError && <div style={{ color: "crimson" }}>Comments failed: {commentsError}</div>}
                    {!commentsLoading && comments && comments.length === 0 && <div className="text-muted">No comments available</div>}
                    {comments && comments.slice(0, 4).map((c, i) => (
                      <div key={i} style={{ marginTop: 8, padding: 8, background: "#fafafa", borderRadius: 8 }}>
                        <strong>{c.author}</strong>
                        <div dangerouslySetInnerHTML={{ __html: c.text }} />
                        <small style={{ color: "#777" }}>{c.published}</small>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

      </main>
    </div>
  );
}
