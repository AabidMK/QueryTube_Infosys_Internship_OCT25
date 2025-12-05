// src/pages/Home.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container" data-testid="home-page">
      <div className="home-hero">

        {/* LEFT CONTENT */}
        <div className="hero-content" data-testid="home-content">
          <h1 className="hero-headline" data-testid="home-title">
            Discover Smarter Insights<br />From Every Video
          </h1>

          <p className="hero-subheading" data-testid="home-subtitle">
            AI-powered understanding beyond keyword search.
          </p>

          <div className="hero-buttons" data-testid="home-actions">
            <button
              className="btn-primary"
              onClick={() => navigate("/search")}
              data-testid="start-search-btn"
            >
              Start Searching
            </button>

            <button
              className="btn-secondary"
              onClick={() => navigate("/upload")}
              data-testid="upload-dataset-btn"
            >
              Upload Dataset
            </button>
          </div>
        </div>

        {/* RIGHT ANIMATION */}
        <div className="hero-visual" data-testid="home-graphic">
          <div className="neural-pattern">
            <div className="golden-orbit orbit-1"></div>
            <div className="golden-orbit orbit-2"></div>
            <div className="golden-orbit orbit-3"></div>
            <div className="core-glow"></div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Home;
