import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Download,
  ContentCopy,
  Refresh,
  AutoAwesome,
  Summarize
} from '@mui/icons-material';
import { summarizeVideo, testSummary } from '../services/api';

const SummaryPage = () => {
  const [videoId, setVideoId] = useState('');
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [useAI, setUseAI] = useState(true);

  const exampleVideos = [
    { id: 't8txtQkhMcY', title: 'Mystery Mountain', channel: 'BRIGHT SIDE' },
    { id: 'mmIidOoHCfs', title: 'Pirate Treasure', channel: 'Discovery' },
    { id: 'CvTsL-WcrgQ', title: 'Killer Waves', channel: 'National Geographic' },
    { id: 'H8SAmnrwSfk', title: 'Terrifying Snakes', channel: 'Animal Planet' },
  ];

  const handleSummarize = async () => {
    if (!videoId.trim()) {
      setError('Please enter a video ID');
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);

    try {
      const response = await summarizeVideo(videoId, useAI, false);
      setSummary(response);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
      console.error('Summarize error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleId) => {
    setVideoId(exampleId);
  };

  const handleCopySummary = () => {
    if (summary?.summary) {
      navigator.clipboard.writeText(summary.summary);
      // Show toast notification (you can implement this)
    }
  };

  const handleDownload = () => {
    if (summary) {
      const blob = new Blob([JSON.stringify(summary, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `summary_${summary.video_id}_${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 3, mt: 8 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ mb: 1 }}>
          AI Video Summarizer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate AI-powered summaries for any YouTube video in your database
        </Typography>
      </Box>

      {/* Input Section */}
      <Paper sx={{ p: 3, mb: 4, backgroundColor: '#212121' }}>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="YouTube Video ID"
              value={videoId}
              onChange={(e) => setVideoId(e.target.value)}
              placeholder="Enter video ID (e.g., t8txtQkhMcY)"
              variant="outlined"
              sx={{ mb: 2 }}
            />
            
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Chip
                icon={<AutoAwesome />}
                label="AI Summarization"
                onClick={() => setUseAI(true)}
                color={useAI ? 'primary' : 'default'}
                variant={useAI ? 'filled' : 'outlined'}
              />
              <Chip
                label="Basic Summary"
                onClick={() => setUseAI(false)}
                color={!useAI ? 'primary' : 'default'}
                variant={!useAI ? 'filled' : 'outlined'}
              />
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <Summarize />}
              onClick={handleSummarize}
              disabled={loading || !videoId.trim()}
              sx={{
                backgroundColor: '#FF0000',
                py: 1.5,
                '&:hover': {
                  backgroundColor: '#CC0000'
                }
              }}
            >
              {loading ? 'Summarizing...' : 'Generate Summary'}
            </Button>
          </Grid>
        </Grid>

        {/* Example Videos */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Try with example videos:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {exampleVideos.map((example) => (
              <Chip
                key={example.id}
                label={`${example.title} (${example.id})`}
                onClick={() => handleExampleClick(example.id)}
                sx={{
                  '&:hover': {
                    backgroundColor: 'rgba(255, 0, 0, 0.2)'
                  }
                }}
              />
            ))}
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={() => setError(null)}>
              Dismiss
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {/* Summary Display */}
      {summary && (
        <Paper sx={{ p: 3, backgroundColor: '#212121' }}>
          {/* Summary Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box>
              <Typography variant="h5" sx={{ mb: 1 }}>
                {summary.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                <Typography variant="body2" color="text.secondary">
                  {summary.channel}
                </Typography>
                <Chip 
                  label={`${useAI ? 'AI' : 'Basic'} Summary`} 
                  size="small" 
                  color={useAI ? 'primary' : 'default'}
                />
                <Typography variant="body2" color="text.secondary">
                  {summary.views.toLocaleString()} views • {summary.duration}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Copy Summary">
                <IconButton onClick={handleCopySummary}>
                  <ContentCopy />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download JSON">
                <IconButton onClick={handleDownload}>
                  <Download />
                </IconButton>
              </Tooltip>
              <Tooltip title="Watch on YouTube">
                <IconButton 
                  onClick={() => window.open(`https://youtube.com/watch?v=${summary.video_id}`, '_blank')}
                  sx={{ backgroundColor: '#FF0000', color: 'white', '&:hover': { backgroundColor: '#CC0000' } }}
                >
                  <PlayArrow />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          <Divider sx={{ mb: 3, borderColor: '#333' }} />

          {/* Summary Content */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Summarize /> Video Summary
            </Typography>
            <Paper sx={{ p: 3, backgroundColor: '#1C1C1C', borderRadius: 2 }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                {summary.summary}
              </Typography>
            </Paper>
          </Box>

          {/* Transcript Excerpt */}
          {summary.transcript_excerpt && (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Transcript Excerpt
              </Typography>
              <Paper sx={{ p: 3, backgroundColor: '#1C1C1C', borderRadius: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                  {summary.transcript_excerpt}
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Metadata */}
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Video Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Typography variant="caption" color="text.secondary">
                  Video ID
                </Typography>
                <Typography variant="body2">
                  {summary.video_id}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="caption" color="text.secondary">
                  Duration
                </Typography>
                <Typography variant="body2">
                  {summary.duration}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="caption" color="text.secondary">
                  Views
                </Typography>
                <Typography variant="body2">
                  {summary.views.toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="caption" color="text.secondary">
                  Generated
                </Typography>
                <Typography variant="body2">
                  {new Date(summary.created_at).toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </Paper>
      )}

      {/* No Summary State */}
      {!summary && !loading && !error && (
        <Paper sx={{ p: 6, textAlign: 'center', backgroundColor: '#212121' }}>
          <AutoAwesome sx={{ fontSize: 60, color: '#666', mb: 2 }} />
          <Typography variant="h6" sx={{ mb: 1 }}>
            Generate Your First Summary
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Enter a YouTube Video ID above and click "Generate Summary" to get started
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default SummaryPage;