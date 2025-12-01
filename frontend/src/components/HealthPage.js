import React, { useState, useEffect } from 'react';
import { healthAPI } from '../services/api';

const HealthPage = () => {
  const [healthData, setHealthData] = useState(null);
  const [apiInfo, setApiInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const [healthResponse, infoResponse] = await Promise.all([
        healthAPI.check(),
        healthAPI.getInfo()
      ]);
      
      setHealthData(healthResponse);
      setApiInfo(infoResponse);
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
          <div style={{ 
            color: 'var(--error-color)', 
            padding: '2rem', 
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            borderRadius: '12px',
            border: '1px solid var(--error-color)',
            textAlign: 'center'
          }}>
            {error}
          </div>
        ) : (
          <div className="health-card">
            <div className="health-status">
              <div className={`status-indicator ${healthData?.status === 'healthy' ? 'status-healthy' : 'status-error'}`}></div>
              <div>
                <h3>API Status: {healthData?.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}</h3>
                <p>Last checked: {new Date().toLocaleString()}</p>
              </div>
            </div>

            <div className="health-details">
              <div className="health-item">
                <div className="health-label">API Version</div>
                <div className="health-value">{apiInfo?.version || healthData?.api_version}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Total Videos</div>
                <div className="health-value">{healthData?.total_videos || 0}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Search Engine</div>
                <div className="health-value">{apiInfo?.search_engine || 'SentenceTransformer'}</div>
              </div>
              
              <div className="health-item">
                <div className="health-label">Search Engine Status</div>
                <div className="health-value">
                  {healthData?.search_engine_ready ? '✅ Ready' : '❌ Not Ready'}
                </div>
              </div>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <button 
                onClick={fetchHealthData}
                className="search-button"
                style={{ padding: '0.8rem 1.5rem' }}
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>
        )}

        <div style={{ marginTop: '2rem', color: 'var(--text-secondary)' }}>
          <h3>API Endpoints</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
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