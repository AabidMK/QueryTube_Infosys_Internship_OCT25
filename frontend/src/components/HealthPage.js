import React, { useState, useEffect } from 'react';
import { healthAPI } from '../services/api';

const HealthPage = () => {
  const [healthData, setHealthData] = useState(null);
  const [apiInfo, setApiInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastChecked, setLastChecked] = useState(null);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const [healthResponse, infoResponse] = await Promise.all([
        healthAPI.check(),
        healthAPI.getInfo()
      ]);
      
      console.log('API Response - Health:', healthResponse);
      console.log('API Response - Info:', infoResponse);
      
      setHealthData(healthResponse);
      setApiInfo(infoResponse);
      setLastChecked(new Date());
      setError('');
    } catch (err) {
      setError('Failed to fetch health data');
      console.error('Health check error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
  }, []);

  // Helper function to get API status
  const getApiStatus = () => {
    if (!healthData) return { status: 'unknown', isHealthy: false };
    
    const status = healthData.status?.toLowerCase() || 'unknown';
    const isHealthy = status === 'healthy' || status === 'operational';
    
    return {
      status: status.charAt(0).toUpperCase() + status.slice(1),
      isHealthy
    };
  };

  // Helper function to get search engine status
  const getSearchEngineStatus = () => {
    if (!healthData) return { status: 'unknown', isReady: false };
    
    // Check different possible locations for model status
    const modelStatus = 
      healthData.database?.model_status?.toLowerCase() ||
      healthData.model_status?.toLowerCase() ||
      healthData.search_engine_status?.toLowerCase() ||
      'unknown';
    
    const isReady = modelStatus === 'ready' || modelStatus === 'loaded' || modelStatus === 'healthy';
    
    return {
      status: modelStatus.charAt(0).toUpperCase() + modelStatus.slice(1),
      isReady
    };
  };

  // Get total videos count
  const getTotalVideos = () => {
    if (!healthData) return 0;
    
    return (
      healthData.database?.total_videos ||
      healthData.total_videos ||
      healthData.total_vectors ||
      0
    );
  };

  // Get API version
  const getApiVersion = () => {
    if (!healthData && !apiInfo) return '1.0.0';
    
    return (
      healthData?.api_version ||
      apiInfo?.version ||
      '1.0.0'
    );
  };

  // Get search engine type
  const getSearchEngine = () => {
    if (!healthData && !apiInfo) return 'SentenceTransformer';
    
    return (
      apiInfo?.search_engine ||
      healthData?.search_engine ||
      'SentenceTransformer + Cosine Similarity'
    );
  };

  const apiStatus = getApiStatus();
  const searchEngineStatus = getSearchEngineStatus();
  const totalVideos = getTotalVideos();
  const apiVersion = getApiVersion();
  const searchEngine = getSearchEngine();

  if (loading) {
    return (
      <div className="health-page">
        <div className="page-header">
          <h1 className="page-title">System Health</h1>
          <p className="page-subtitle">Checking API status and system information</p>
        </div>
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="health-page">
      <div className="page-header">
        <h1 className="page-title">System Health</h1>
        <p className="page-subtitle">API status and system information</p>
      </div>

      <div className="health-container">
        {error ? (
          <div className="health-error">
            {error}
          </div>
        ) : (
          <div className="health-card">
            <div className="health-status">
              <div className={`status-indicator ${apiStatus.isHealthy ? 'status-healthy' : 'status-error'}`}></div>
              <div>
                <h3>API Status: {apiStatus.isHealthy ? '✅ Healthy' : '❌ ' + apiStatus.status}</h3>
                <p>Last checked: {lastChecked ? lastChecked.toLocaleString() : 'Never'}</p>
              </div>
            </div>

            <div className="health-details">
              <div className="health-item">
                <div className="health-label">API Version</div>
                <div className="health-value">{apiVersion}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Total Videos</div>
                <div className="health-value">{totalVideos}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Search Engine</div>
                <div className="health-value">{searchEngine}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Search Engine Status</div>
                <div className="health-value">
                  {searchEngineStatus.isReady ? '✅ Ready' : '❌ ' + searchEngineStatus.status}
                </div>
              </div>
            </div>

            {/* Additional Database Information */}
            {healthData?.database && (
              <div className="database-details">
                <h4>Database Details</h4>
                <div className="health-details">
                  <div className="health-item">
                    <div className="health-label">Model Loaded</div>
                    <div className="health-value">
                      {healthData.database.model_loaded ? '✅ Yes' : '❌ No'}
                    </div>
                  </div>
                  <div className="health-item">
                    <div className="health-label">FAISS Loaded</div>
                    <div className="health-value">
                      {healthData.database.faiss_loaded ? '✅ Yes' : '❌ No'}
                    </div>
                  </div>
                  <div className="health-item">
                    <div className="health-label">Environment</div>
                    <div className="health-value">{healthData.database.environment || 'Unknown'}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Display Raw Data for Debugging */}
            <details className="debug-info">
              <summary>Debug Information</summary>
              <div className="debug-content">
                <strong>Health Data:</strong>
                <pre>
                  {JSON.stringify(healthData, null, 2)}
                </pre>
                <strong>API Info:</strong>
                <pre>
                  {JSON.stringify(apiInfo, null, 2)}
                </pre>
              </div>
            </details>

            <div className="refresh-button-container">
              <button 
                onClick={fetchHealthData}
                className="search-button refresh-button"
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>
        )}

        <div className="api-endpoints">
          <h3>API Endpoints</h3>
          <ul className="endpoints-list">
            <li>🔍 <strong>POST /api/search</strong> - Semantic video search</li>
            <li>📤 <strong>POST /api/ingest</strong> - Upload CSV data</li>
            <li>💓 <strong>GET /api/health</strong> - Health check</li>
            <li>ℹ️ <strong>GET /api/</strong> - API information</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default HealthPage;