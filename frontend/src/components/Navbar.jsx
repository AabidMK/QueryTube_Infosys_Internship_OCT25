// Navbar.jsx
import React from "react";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <div className="brand" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <a href="/" className="brand-title">QueryTube</a>
          <span className="brand-sub">Semantic Video Search</span>
        </div>

        <nav className="nav-links" aria-label="Main navigation">
          <a href="/">Home</a>
          <a href="/search">Ingest CSV</a>
          <a href="/summarize">Summary</a>
        </nav>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{ width: 10, height: 10, borderRadius: 20, background: "linear-gradient(90deg,#f97316,#ef4444)", boxShadow: "0 6px 18px rgba(239,68,68,0.12)" }} title="live"></div>
        </div>
      </div>
    </header>
  );
}
