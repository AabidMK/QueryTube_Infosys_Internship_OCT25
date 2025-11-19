import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  Container,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SummarizeIcon from '@mui/icons-material/Summarize';
import CloseIcon from '@mui/icons-material/Close';
import api from '../api';

// Helper function to format duration
const formatDuration = (seconds) => {
  if (!seconds) return 'N/A';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
};

function SearchVideos() {
  const [searchQuery, setSearchQuery] = useState('');
  const [databases, setDatabases] = useState([]);
  const [selectedDb, setSelectedDb] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [summaryDialog, setSummaryDialog] = useState({
    open: false,
    videoId: null,
    summary: '',
    loading: false,
    error: null,
  });

  // Fetch available databases
  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const response = await api.get('/health');
        const dbs = response.data.databases || [];
        setDatabases(dbs);
        if (dbs.length > 0) {
          setSelectedDb(dbs[0].name);
        }
      } catch (err) {
        console.error('Error loading databases:', err);
        setError('Failed to load databases');
      }
    };

    fetchDatabases();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim() || !selectedDb) return;

    setLoading(true);
    setError('');
    
    try {
      const response = await api.get(
        `/search?collection_name=${encodeURIComponent(selectedDb)}&query=${encodeURIComponent(searchQuery)}`
      );
      
      // Handle both array and object with results property
      const results = Array.isArray(response.data) 
        ? response.data 
        : (response.data?.results || []);
      
      setSearchResults(results);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to perform search');
      console.error('Search error:', err);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (result) => {
  console.log('Summarize clicked for video:', result.video_id || result.id);
  
  if (!result || !selectedDb) {
    console.error('Missing video data or selected database');
    return;
  }

  setSummaryDialog({
    open: true,
    videoId: result.video_id || result.id,
    loading: true,
    summary: '',
    error: null
  });

  try {
    console.log('Sending request to summarize...');
    const response = await api.post('/summarize', {
      video_id: result.video_id || result.id,
      collection_name: selectedDb
      // Don't send the transcript, let backend fetch it
    });
    
    console.log('Received summary:', response.data);
    setSummaryDialog(prev => ({
      ...prev,
      summary: response.data.summary || 'No summary available',
      loading: false
    }));
  } catch (err) {
    console.error('Summarization error:', err);
    const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate summary';
    console.error('Error details:', errorMessage);
    
    setSummaryDialog(prev => ({
      ...prev,
      error: errorMessage,
      loading: false,
      summary: ''
    }));
  }
};

      
  
  const handleCloseSummary = () => {
    setSummaryDialog({
      open: false,
      videoId: null,
      summary: '',
      loading: false,
      error: null,
    });
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Search Videos
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={5}>
            <TextField
              fullWidth
              label="Search query"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter your search query..."
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel id="database-select-label">Database</InputLabel>
              <Select
                labelId="database-select-label"
                value={selectedDb}
                label="Database"
                onChange={(e) => setSelectedDb(e.target.value)}
              >
                {databases.map((db) => (
                  <MenuItem key={db.name} value={db.name}>
                    {db.name} ({db.record_count || 0} videos)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              fullWidth
              variant="contained"
              color="primary"
              size="large"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={!searchQuery.trim() || !selectedDb || loading}
              sx={{ height: '56px' }}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}

      {!loading && searchResults.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Found {searchResults.length} results
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Grid container spacing={3}>
            {searchResults.map((result) => (
              <Grid item xs={12} key={result.video_id || result.id}>
                <Card sx={{ display: 'flex', height: '200px' }}>
                  <CardMedia
                    component="img"
                    sx={{ 
                      width: 300, 
                      objectFit: 'cover',
                      cursor: 'pointer'
                    }}
                    image={result.thumbnail || `https://img.youtube.com/vi/${result.video_id || result.id}/hqdefault.jpg`}
                    alt={result.title}
                    onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                  />
                  <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                    <CardContent sx={{ flex: '1 0 auto' }}>
                      <Typography 
                        component="div" 
                        variant="h6"
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { textDecoration: 'underline' }
                        }}
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                      >
                        {result.title}
                      </Typography>
                      <Typography 
                        variant="subtitle1" 
                        color="text.secondary" 
                        component="div"
                        sx={{ 
                          cursor: 'pointer',
                          '&:hover': { textDecoration: 'underline' }
                        }}
                        onClick={() => window.open(`https://www.youtube.com/channel/${result.channel_id || ''}`, '_blank')}
                      >
                        {result.channel || result.channel_title}
                      </Typography>
                      <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {result.view_count !== undefined && (
                          <Chip
                            size="small"
                            label={`👁️ ${parseInt(result.view_count || 0).toLocaleString()} views`}
                            variant="outlined"
                          />
                        )}
                        {result.duration_seconds && (
                          <Chip
                            size="small"
                            label={`⏱️ ${formatDuration(result.duration_seconds)}`}
                            variant="outlined"
                          />
                        )}
                        {result.similarity_score !== undefined && (
                          <Chip
                            size="small"
                            color="primary"
                            label={`Relevance: ${(result.similarity_score * 100).toFixed(1)}%`}
                            variant="outlined"
                          />
                        )}
                      </Box>
                      {result.transcript && (
                        <Typography 
                          variant="body2" 
                          color="text.secondary" 
                          sx={{ 
                            mt: 1,
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                          }}
                        >
                          {result.transcript}
                        </Typography>
                      )}
                    </CardContent>
                    <Box sx={{ p: 2, pt: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      
                          <Tooltip title="Generate summary">
                            <span> {/* Wrapper span for tooltip to work properly */}
                              <Button
                                size="small"
                                color="secondary"
                                variant="outlined"
                                onClick={(e) => {
                                  e.preventDefault();
                                  e.stopPropagation();
                                  handleSummarize(result);
                                }}
                                startIcon={<SummarizeIcon />}
                                sx={{ whiteSpace: 'nowrap' }}
                              >
                                Summarize
                              </Button>
                            </span>
                          </Tooltip>
                      <Button
                        size="small"
                        color="primary"
                        variant="contained"
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                        startIcon={<PlayArrowIcon />}
                      >
                        Watch
                      </Button>
                    </Box>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {!loading && searchQuery && searchResults.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="textSecondary">
            No results found for "{searchQuery}"
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mt: 1 }}>
            Try different keywords or check your search query.
          </Typography>
        </Box>
      )}

      {/* Summary Dialog */}
      <Dialog 
        open={summaryDialog.open} 
        onClose={handleCloseSummary}
        maxWidth="md"
        fullWidth
        aria-labelledby="summary-dialog-title"
        aria-describedby="summary-dialog-description"
      >
        <DialogTitle id="summary-dialog-title">
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" component="span">
              Video Summary
            </Typography>
            <IconButton 
              onClick={handleCloseSummary} 
              size="small"
              aria-label="close"
              sx={{ ml: 2 }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {summaryDialog.loading ? (
            <Box display="flex" justifyContent="center" my={4} flexDirection="column" alignItems="center">
              <CircularProgress />
              <Typography variant="body1" sx={{ mt: 2 }}>
                Generating summary...
              </Typography>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                This may take a few moments.
              </Typography>
            </Box>
          ) : summaryDialog.error ? (
            <Alert 
              severity="error" 
              sx={{ my: 2 }}
              action={
                <IconButton
                  aria-label="close"
                  color="inherit"
                  size="small"
                  onClick={handleCloseSummary}
                >
                  <CloseIcon fontSize="inherit" />
                </IconButton>
              }
            >
              <Box>
                <Typography variant="subtitle2">Error generating summary</Typography>
                <Typography variant="body2">{summaryDialog.error}</Typography>
              </Box>
            </Alert>
          ) : (
            <Box sx={{ mt: 1, maxHeight: '60vh', overflowY: 'auto' }}>
              <ReactMarkdown
                components={{
                  p: ({node, ...props}) => <Typography paragraph {...props} sx={{ mb: 2, lineHeight: 1.6 }} />,
                  h1: ({node, ...props}) => <Typography variant="h4" gutterBottom {...props} />,
                  h2: ({node, ...props}) => <Typography variant="h5" gutterBottom {...props} />,
                  h3: ({node, ...props}) => <Typography variant="h6" gutterBottom {...props} />,
                  li: ({node, ...props}) => <li {...props} style={{marginBottom: 8}} />,
                  a: ({node, ...props}) => <a {...props} target="_blank" rel="noopener noreferrer" style={{color: '#1976d2'}} />
                }}
                sx={{
                  '& > *': {
                    mb: 2,
                    '&:last-child': { mb: 0 }
                  },
                  '& ul, & ol': {
                    pl: 3,
                    mb: 2
                  },
                  '& p': {
                    mb: 2
                  }
                }}
              >
                {summaryDialog.summary}
              </ReactMarkdown>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button 
            onClick={handleCloseSummary} 
            color="primary"
            variant="outlined"
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default SearchVideos;