// src/components/Navbar.jsx

import React from "react";
import { Link } from "react-router-dom";
import { Sparkles } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="navbar" data-testid="main-navbar">

      {/* Left Section */}
      <div className="navbar-left" data-testid="navbar-logo">
        <div className="logo-icon">
          <Sparkles className="sparkle-icon" size={20} />
        </div>
        <span className="navbar-brand">QueryTube AI</span>
      </div>

      {/* Right Links */}
      <div className="navbar-links" data-testid="navbar-links">
        <Link to="/" className="nav-link" data-testid="nav-home">Home</Link>
        <Link to="/search" className="nav-link" data-testid="nav-search">Search</Link>
        <Link to="/upload" className="nav-link" data-testid="nav-upload">Upload</Link>
        <Link to="/summary" className="nav-link" data-testid="nav-summary">Summary</Link>
      </div>

    </nav>
  );
};

export default Navbar;
