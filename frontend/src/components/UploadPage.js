import React, { useState } from 'react';
import { uploadAPI } from '../services/api';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid CSV file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a CSV file to upload');
      return;
    }

    setUploading(true);
    setError('');
    setResult(null);

    try {
      const uploadResult = await uploadAPI.ingest(file);
      setResult(uploadResult);
      setFile(null);
      // Reset file input
      document.getElementById('file-input').value = '';
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload file');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1 className="page-title">Upload CSV Data</h1>
        <p className="page-subtitle">
          Upload YouTube video data in CSV format for semantic search
        </p>
      </div>

      <div className="upload-container">
        <form onSubmit={handleUpload} className="upload-form">
          <div
            className={`upload-area ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              {file ? `Selected: ${file.name}` : 'Drag & drop your CSV file here or click to browse'}
            </div>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="file-input"
            />
          </div>

          <button 
            type="submit" 
            className="upload-button"
            disabled={uploading || !file}
          >
            {uploading ? '📤 Uploading...' : '🚀 Upload CSV'}
          </button>

          {error && (
            <div style={{ 
              color: 'var(--error-color)', 
              marginTop: '1rem', 
              padding: '1rem', 
              backgroundColor: 'rgba(244, 67, 54, 0.1)',
              borderRadius: '8px',
              border: '1px solid var(--error-color)'
            }}>
              {error}
            </div>
          )}

          {result && (
            <div style={{ 
              color: 'var(--success-color)', 
              marginTop: '1rem', 
              padding: '1rem', 
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              borderRadius: '8px',
              border: '1px solid var(--success-color)'
            }}>
              <h4>✅ Upload Successful!</h4>
              <p><strong>Message:</strong> {result.message}</p>
              <p><strong>Ingested:</strong> {result.ingested_count} documents</p>
              <p><strong>Errors:</strong> {result.error_count}</p>
              <p><strong>Timestamp:</strong> {new Date(result.timestamp).toLocaleString()}</p>
            </div>
          )}
        </form>

        <div className="upload-info">
          <h4>📋 CSV Format Requirements</h4>
          <p>Your CSV file should include the following columns:</p>
          <ul>
            <li><strong>transcript</strong> (required) - Video transcript text</li>
            <li><strong>id</strong> (optional) - Video ID</li>
            <li><strong>title</strong> (optional) - Video title</li>
            <li><strong>channel_title</strong> (optional) - Channel name</li>
            <li><strong>view_count</strong> (optional) - View count</li>
            <li><strong>duration</strong> (optional) - Video duration</li>
          </ul>
          <p><em>Note: Only the 'transcript' column is strictly required for semantic search.</em></p>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;