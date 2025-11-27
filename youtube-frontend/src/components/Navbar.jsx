import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function Navbar(){
  const loc = useLocation();
  return (
    <div className="navbar">
      <div className="nav-left">
        <div className="logo">
          <div className="dot" />
          <div>Youtube Semantic Search</div>
        </div>
        <div style={{marginLeft:12, color:"rgba(255,255,255,0.85)"}}>Search</div>
      </div>

      <div className="nav-links">
        <Link to="/upload" style={loc.pathname === "/upload" ? {fontWeight:700} : {}}>Upload</Link>
        <Link to="/results" style={loc.pathname === "/results" ? {fontWeight:700} : {}}>Results</Link>
        <a href="https://www.youtube.com" target="_blank" rel="noreferrer">YouTube</a>
      </div>
    </div>
  );
}
