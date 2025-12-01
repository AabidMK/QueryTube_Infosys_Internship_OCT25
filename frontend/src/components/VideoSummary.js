import React, { useState, useEffect } from 'react';
import { summaryAPI } from '../services/api';


const VideoSummary = ({ videoId, onClose }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await summaryAPI.getSummary(videoId);
        setSummary(data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch video summary');
        console.error('Error fetching summary:', err);
      } finally {
        setLoading(false);
      }
    };

    if (videoId) {
      fetchSummary();
    }
  }, [videoId]);

  const formatCount = (count) => {
    if (typeof count === 'number') {
      if (count >= 1000000) {
        return (count / 1000000).toFixed(1) + 'M';
      } else if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K';
      }
      return count.toString();
    }
    return count || 'N/A';
  };

  const getVideoUrl = (videoId) => {
    return `https://www.youtube.com/watch?v=${videoId}`;
  };

  if (loading) {
    return (
      <div className="video-summary-overlay">
        <div className="video-summary-modal">
          <div className="summary-loading">
            <div className="loading-spinner"></div>
            <p>Generating AI summary...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="video-summary-overlay">
        <div className="video-summary-modal">
          <div className="summary-error">
            <h3>❌ Error</h3>
            <p>{error}</p>
            
          </div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <div className="video-summary-overlay">
      <div className="video-summary-modal">
        <div className="summary-header">
          <h2>Video Summary</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="summary-content">
          {/* Basic Video Info */}
          <div className="video-basic-info">
            <h3 className="summary-title">{summary.title}</h3>
            <div className="video-meta">
              <span className="channel">📺 {summary.channel}</span>
              <span className="views">👁️ {formatCount(summary.views)} views</span>
              <span className="duration">⏱️ {summary.duration}</span>
            </div>
          </div>

          {/* Statistics */}
          <div className="statistics-section">
            <h4>📊 Video Statistics</h4>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Transcript Length:</span>
                <span className="stat-value">{summary.statistics.transcript_length} chars</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Word Count:</span>
                <span className="stat-value">{summary.statistics.word_count} words</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Sentence Count:</span>
                <span className="stat-value">{summary.statistics.sentence_count} sentences</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Avg Word Length:</span>
                <span className="stat-value">{summary.statistics.avg_word_length?.toFixed(1)} chars</span>
              </div>
            </div>
          </div>

          {/* AI Summary */}
          <div className="ai-summary-section">
            <h4>🤖 AI-Generated Summary</h4>
            <div className="summary-text">
              {summary.summary.split('\n').map((paragraph, index) => (
                <p key={index}>{paragraph}</p>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="summary-actions">
            <a 
              href={getVideoUrl(summary.id)} 
              target="_blank" 
              rel="noopener noreferrer"
              className="watch-button"
            >
              ▶️ Watch on YouTube
            </a>
            
          </div>

          <div className="summary-footer">
            <small>Generated at: {new Date(summary.generated_at).toLocaleString()}</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoSummary;