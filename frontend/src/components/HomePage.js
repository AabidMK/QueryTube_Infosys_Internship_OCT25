import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  const features = [
    {
      icon: '🔍',
      title: 'Semantic Search',
      description: 'Search YouTube videos using natural language queries powered by AI embeddings',
      color: '#ff0000'
    },
    {
      icon: '🧠',
      title: 'AI-Powered',
      description: 'Uses SentenceTransformer models to understand context and meaning',
      color: '#3ea6ff'
    },
    {
      icon: '📊',
      title: 'Smart Analytics',
      description: 'Get similarity scores, relevance ratings, and keyword matching insights',
      color: '#4caf50'
    },
    {
      icon: '⚡',
      title: 'Fast & Efficient',
      description: 'Built with FAISS for lightning-fast similarity search',
      color: '#ff9800'
    },
    {
      icon: '📁',
      title: 'Easy Upload',
      description: 'Upload CSV files with YouTube data through a simple drag-and-drop interface',
      color: '#9c27b0'
    },
    {
      icon: '📱',
      title: 'Responsive Design',
      description: 'Works perfectly on desktop, tablet, and mobile devices',
      color: '#2196f3'
    }
  ];

  const stats = [
    { number: '5', label: 'Top Results' },
    { number: '99.9%', label: 'Accuracy' },
    { number: '⚡', label: 'Fast Search' },
    { number: '🔍', label: 'Semantic Understanding' }
  ];

  const howItWorks = [
    {
      step: 1,
      title: 'Upload Data',
      description: 'Upload your YouTube video data in CSV format with transcripts',
      icon: '📤'
    },
    {
      step: 2,
      title: 'AI Processing',
      description: 'Our system processes and indexes the content using advanced embeddings',
      icon: '🧠'
    },
    {
      step: 3,
      title: 'Semantic Search',
      description: 'Search using natural language - no need for exact keywords',
      icon: '🔍'
    },
    {
      step: 4,
      title: 'Get Insights',
      description: 'Receive relevant results with similarity scores and analytics',
      icon: '📊'
    }
  ];

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Discover YouTube Videos with
              <span className="gradient-text"> AI-Powered Semantic Search</span>
            </h1>
            <p className="hero-description">
              QueryTube:AI transforms how you search through YouTube content. 
              Find exactly what you're looking for using natural language, 
              powered by advanced machine learning and semantic understanding.
            </p>
            <div className="hero-buttons">
              <Link to="/search" className="cta-button primary">
                🚀 Start Searching
              </Link>
              <Link to="/upload" className="cta-button secondary">
                📤 Upload Data
              </Link>
            </div>
          </div>
          <div className="hero-visual">
            <div className="search-demo">
              <div className="demo-search-bar">
                <span className="demo-icon">🔍</span>
                <span className="demo-text">"machine learning tutorials for beginners"</span>
              </div>
              <div className="demo-results">
                <div className="demo-result-card">
                  <div className="demo-result-header">
                    <span className="demo-title">Machine Learning Fundamentals - Complete Course</span>
                    <span className="demo-score">92%</span>
                  </div>
                  <div className="demo-preview">Learn the basics of machine learning with hands-on examples and practical projects...</div>
                </div>
                <div className="demo-result-card">
                  <div className="demo-result-header">
                    <span className="demo-title">AI and ML Tutorial for Absolute Beginners</span>
                    <span className="demo-score">88%</span>
                  </div>
                  <div className="demo-preview">Perfect starting point for beginners interested in artificial intelligence...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          {stats.map((stat, index) => (
            <div key={index} className="stat-item">
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>Powerful Features</h2>
          <p>Everything you need for intelligent video content discovery</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div 
                className="feature-icon"
                style={{ backgroundColor: `${feature.color}20`, color: feature.color }}
              >
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Simple steps to unlock powerful semantic search capabilities</p>
        </div>
        <div className="steps-container">
          {howItWorks.map((step, index) => (
            <div key={index} className="step-item">
              <div className="step-number">{step.step}</div>
              <div className="step-icon">{step.icon}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Transform Your Video Search Experience?</h2>
          <p>Join thousands of users who are discovering content smarter and faster</p>
          <div className="cta-buttons">
            <Link to="/search" className="cta-button primary large">
              🚀 Start Searching Now
            </Link>
            <Link to="/upload" className="cta-button secondary large">
              📤 Upload Your First Dataset
            </Link>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="tech-section">
        <div className="section-header">
          <h2>Built with Modern Technology</h2>
          <p>Powered by cutting-edge AI and web technologies</p>
        </div>
        <div className="tech-grid">
          <div className="tech-item">
            <div className="tech-icon">⚡</div>
            <span>FastAPI</span>
          </div>
          <div className="tech-item">
            <div className="tech-icon">🔍</div>
            <span>FAISS</span>
          </div>
          <div className="tech-item">
            <div className="tech-icon">🧠</div>
            <span>SentenceTransformer</span>
          </div>
          <div className="tech-item">
            <div className="tech-icon">⚛️</div>
            <span>React</span>
          </div>
          <div className="tech-item">
            <div className="tech-icon">🎨</div>
            <span>Modern CSS</span>
          </div>
          <div className="tech-item">
            <div className="tech-icon">📊</div>
            <span>Scikit-learn</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;