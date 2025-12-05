// ChannelVideos.jsx
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiGet } from "../api/api";

const DEFAULT_THUMB = "/mnt/data/b9f0aca2-0574-4170-9d41-39b3128f898c.png";

export default function ChannelVideos() {
  const { channelName } = useParams();
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    if (!channelName) return;
    apiGet(`/videos-by-channel/${channelName}`)
      .then(d => setVideos(d.videos || []))
      .catch(() => setVideos([]));
  }, [channelName]);

  function pickThumb(v) {
    if (v.thumbnail) return v.thumbnail;
    const id = v.video_id || v.id;
    if (id) return `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
    return DEFAULT_THUMB;
  }

  return (
    <div className="pt-28 max-w-6xl mx-auto px-6">
      <h1 className="text-3xl font-bold mb-6" style={{color:"#111827"}}>{channelName}</h1>
      <div className="grid md:grid-cols-3 gap-6">
        {videos.map(v => {
          const vid = v.video_id || v.id;
          const thumb = pickThumb(v);
          return (
            <div key={vid} className="glass-card p-4 rounded-2xl fade-in">
              <div style={{ position: "relative" }}>
                <img src={thumb} alt={v.title} className="w-full h-40 object-cover rounded-lg mb-3" />
                <div style={{ position: "absolute", top: 10, left: 10, background: "linear-gradient(90deg,#ef4444,#f97316)", color:"#fff", padding:"6px 10px", borderRadius:8, fontSize:12, fontWeight:700 }}>Video</div>
              </div>
              <h3 className="font-semibold" style={{color:"#111827"}}>{v.title}</h3>
              <p className="text-xs" style={{color:"#6b7280", marginTop:6}}>ID: {vid}</p>
              {(v.summary || (v.metadata && v.metadata.summary)) && (
                <div style={{ marginTop: 8, color: "#374151", fontSize: 13 }}>
                  {(v.summary || v.metadata.summary).slice(0, 160)}{(v.summary || v.metadata.summary).length > 160 ? "..." : ""}
                </div>
              )}

              <div className="flex gap-2 mt-4">
                <Link to={`/summarize/${encodeURIComponent(vid)}`} className="btn-accent px-3 py-2 rounded-lg" style={{ textDecoration: "none" }}>Summarize</Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
