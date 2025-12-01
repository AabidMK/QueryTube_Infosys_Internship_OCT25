import React, { useState } from 'react';
import VideoCard from './VideoCard';
import VideoSummary from './VideoSummary';
import { searchAPI } from '../services/api';  


const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedVideoId, setSelectedVideoId] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    
    try {
      const searchResults = await searchAPI.search(query, 10);
      setResults(searchResults.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search videos');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoClick = (videoId) => {
    setSelectedVideoId(videoId);
  };

  const handleCloseSummary = () => {
    setSelectedVideoId(null);
  };

  return (
    <div className="search-page">
      <div className="search-container">
        <h1>Semantic Video Search</h1>
        <p className="search-description">
          Search through video transcripts using AI-powered semantic search
        </p>
        
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your search query..."
              className="search-input"
            />
            <button 
              type="submit" 
              className="search-button"
              disabled={loading}
            >
              {loading ? '🔍 Searching...' : '🔍 Search'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="search-stats">
            Found {results.length} results • 
            Average similarity: {(results.reduce((acc, result) => acc + result.similarity_score, 0) / results.length * 100).toFixed(1)}%
          </div>
        )}

        <div className="search-results">
          {results.length > 0 ? (
            results.map((video, index) => (
              <VideoCard 
                key={video.id} 
                video={video} 
                index={index}
                onVideoClick={handleVideoClick}
              />
            ))
          ) : query && !loading ? (
            <div className="no-results">
              <p>No results found for "{query}"</p>
              <p>Try different keywords or upload more videos</p>
            </div>
          ) : null}
        </div>
      </div>

      {selectedVideoId && (
        <VideoSummary 
          videoId={selectedVideoId}
          onClose={handleCloseSummary}
        />
      )}
    </div>
  );
};

export default SearchPage;