import React from 'react';

const VideoCard = ({ video, index, onVideoClick }) => {
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

  const getThumbnailUrl = (videoId, quality = 'medium') => {
    // Different quality options for YouTube thumbnails
    const qualities = {
      default: `https://img.youtube.com/vi/${videoId}/default.jpg`,
      medium: `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`,
      high: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
      standard: `https://img.youtube.com/vi/${videoId}/sddefault.jpg`,
      maxres: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`
    };
    return qualities[quality] || qualities.medium;
  };

  const handleSummaryClick = () => {
    if (onVideoClick) {
      onVideoClick(video.id);
    }
  };

  const handlePlayButtonClick = (e) => {
    e.stopPropagation();
    // Open YouTube video in new tab
    window.open(getVideoUrl(video.id), '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="video-card">
      <div className="video-header">
        <div className="video-rank">{index + 1}</div>
        <div className="video-main-info">
          <h3 className="video-title">
            {video.title}
          </h3>
          <div className="video-channel">
            <span className="channel-icon">📺</span>
            {video.channel}
          </div>
        </div>
      </div>

      {/* Video Thumbnail */}
      <div className="video-thumbnail-container">
        <img 
          src={getThumbnailUrl(video.id)} 
          alt={`${video.title} thumbnail`}
          className="video-thumbnail"
          onClick={handlePlayButtonClick}
          onError={(e) => {
            // Fallback if thumbnail fails to load
            e.target.src = getThumbnailUrl(video.id, 'default');
          }}
        />
        <div className="thumbnail-overlay">
          <button 
            className="play-button"
            onClick={handlePlayButtonClick}
          >
            ▶
          </button>
        </div>
      </div>

      <div className="video-details">
        <div className="detail-row">
          <div className="detail-item">
            <span className="detail-label">Video ID:</span>
            <span className="detail-value video-id">{video.id}</span>
          </div>
        </div>
        
        <div className="detail-row">
          <div className="detail-item">
            <span className="detail-label">👁️ Views:</span>
            <span className="detail-value">{formatCount(video.views)}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">👍 Likes:</span>
            <span className="detail-value">{formatCount(video.likes || video.metadata?.likes)}</span>
          </div>
        </div>
        
        {/* Add similarity score if available */}
        {video.similarity_score && (
          <div className="detail-row">
            <div className="detail-item">
              <span className="detail-label">🎯 Similarity:</span>
              <span className="detail-value similarity-score">
                {(video.similarity_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">📊 Relevance:</span>
              <span className="detail-value relevance-badge">{video.relevance}</span>
            </div>
          </div>
        )}
      </div>

      <div className="video-actions">
        <button 
          className="summary-button"
          onClick={handleSummaryClick}
        >
          📝 View Summary
        </button>
      </div>
    </div>
  );
};

export default VideoCard;