import React, { useState, useEffect } from 'react';
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
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SummarizeIcon from '@mui/icons-material/Summarize';
import CloseIcon from '@mui/icons-material/Close';
import InfoIcon from '@mui/icons-material/Info';
import VisibilityIcon from '@mui/icons-material/Visibility';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
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
  
  // Summary dialog state
  const [summaryDialog, setSummaryDialog] = useState({
    open: false,
    videoId: null,
    summary: '',
    loading: false,
    error: null,
  });

  // Metadata dialog state
  const [metadataDialog, setMetadataDialog] = useState({
    open: false,
    videoId: null,
    metadata: null,
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
    if (!result || !selectedDb) return;

    setSummaryDialog({
      open: true,
      videoId: result.video_id || result.id,
      loading: true,
      summary: '',
      error: null
    });

    try {
      const response = await api.post('/summarize', {
        video_id: result.video_id || result.id,
        collection_name: selectedDb
      });
      
      setSummaryDialog(prev => ({
        ...prev,
        summary: response.data.summary || 'No summary available',
        loading: false
      }));
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate summary';
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

  const handleViewMetadata = async (result) => {
    if (!result || !selectedDb) return;

    setMetadataDialog({
      open: true,
      videoId: result.video_id || result.id,
      metadata: null,
      loading: true,
      error: null
    });

    try {
      const response = await api.get('/video_metadata', {
        params: {
          collection_name: selectedDb,
          video_id: result.video_id || result.id
        }
      });
      
      setMetadataDialog(prev => ({
        ...prev,
        metadata: response.data,
        loading: false
      }));
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch metadata';
      setMetadataDialog(prev => ({
        ...prev,
        error: errorMessage,
        loading: false
      }));
    }
  };

  const handleCloseMetadata = () => {
    setMetadataDialog({
      open: false,
      videoId: null,
      metadata: null,
      loading: false,
      error: null,
    });
  };

  return (
    <Container maxWidth="lg" className="fade-in">
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 800, mt: 2 }}>
        Search Videos
      </Typography>

      <Paper 
        elevation={0}
        sx={{ 
          p: 3, 
          mb: 4, 
          borderRadius: 4, 
          backgroundColor: 'rgba(21, 26, 35, 0.6)', 
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.05)'
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={5}>
            <TextField
              fullWidth
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="What are you looking for?"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: 'text.secondary' }} />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel id="database-select-label">Select Database</InputLabel>
              <Select
                labelId="database-select-label"
                value={selectedDb}
                label="Select Database"
                onChange={(e) => setSelectedDb(e.target.value)}
                sx={{ borderRadius: 3 }}
              >
                {databases.map((db) => (
                  <MenuItem key={db.name} value={db.name}>
                    {db.name} ({db.record_count || 0})
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
              onClick={handleSearch}
              disabled={!searchQuery.trim() || !selectedDb || loading}
              sx={{ height: '56px', borderRadius: 3, fontSize: '1.1rem' }}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" variant="filled" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {loading && (
        <Box display="flex" justifyContent="center" my={8}>
          <CircularProgress size={60} thickness={2} sx={{ color: '#00f2ff' }} />
        </Box>
      )}

      {!loading && searchResults.length > 0 && (
        <Box className="fade-in">
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Found <Box component="span" sx={{ color: '#00f2ff' }}>{searchResults.length}</Box> matches
            </Typography>
          </Box>
          <Divider sx={{ mb: 3, borderColor: 'rgba(255,255,255,0.1)' }} />
          <Grid container spacing={3}>
            {searchResults.map((result) => (
              <Grid item xs={12} key={result.video_id || result.id}>
                <Card 
                    sx={{ 
                        display: 'flex', 
                        height: { xs: 'auto', md: '220px' },
                        flexDirection: { xs: 'column', md: 'row' },
                        overflow: 'visible'
                    }}
                >
                  <Box sx={{ position: 'relative', width: { xs: '100%', md: 320 }, flexShrink: 0 }}>
                    <CardMedia
                        component="img"
                        sx={{ 
                        width: '100%',
                        height: '100%', 
                        objectFit: 'cover',
                        cursor: 'pointer',
                        borderRadius: { xs: '16px 16px 0 0', md: '16px 0 0 16px' }
                        }}
                        image={result.thumbnail || `https://img.youtube.com/vi/${result.video_id || result.id}/hqdefault.jpg`}
                        alt={result.title}
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                    />
                    <Box 
                        sx={{ 
                            position: 'absolute', 
                            inset: 0, 
                            bgcolor: 'rgba(0,0,0,0.3)', 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center',
                            opacity: 0,
                            transition: 'opacity 0.2s',
                            cursor: 'pointer',
                            '&:hover': { opacity: 1 }
                        }}
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                    >
                        <PlayArrowIcon sx={{ fontSize: 60, color: '#fff', filter: 'drop-shadow(0 0 10px rgba(0,0,0,0.5))' }} />
                    </Box>
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, p: 2 }}>
                    <CardContent sx={{ flex: '1 0 auto', p: '0 !important' }}>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                        <Typography 
                            component="div" 
                            variant="h6"
                            sx={{ 
                            cursor: 'pointer',
                            fontWeight: 700,
                            lineHeight: 1.2,
                            mb: 1,
                            '&:hover': { color: '#00f2ff' },
                            transition: 'color 0.2s'
                            }}
                            onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                        >
                            {result.title}
                        </Typography>
                        {result.similarity_score !== undefined && (
                          <Chip
                            size="small"
                            label={`${(result.similarity_score * 100).toFixed(0)}% Match`}
                            sx={{ 
                                bgcolor: 'rgba(0, 242, 255, 0.1)', 
                                color: '#00f2ff', 
                                border: '1px solid rgba(0, 242, 255, 0.3)',
                                fontWeight: 700
                            }}
                          />
                        )}
                      </Box>
                      
                      <Typography 
                        variant="subtitle2" 
                        color="text.secondary" 
                        sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        by <Box component="span" sx={{ color: '#fff' }}>{result.channel || result.channel_title}</Box>
                      </Typography>

                      <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {result.view_count !== undefined && (
                          <Chip
                            size="small"
                            icon={<VisibilityIcon style={{ fontSize: 16 }} />}
                            label={parseInt(result.view_count || 0).toLocaleString()}
                            variant="outlined"
                            sx={{ borderRadius: 1 }}
                          />
                        )}
                        {result.duration_seconds && (
                          <Chip
                            size="small"
                            icon={<AccessTimeIcon style={{ fontSize: 16 }} />}
                            label={formatDuration(result.duration_seconds)}
                            variant="outlined"
                            sx={{ borderRadius: 1 }}
                          />
                        )}
                      </Box>
                      
                      {result.transcript && (
                        <Typography 
                          variant="body2" 
                          color="text.secondary" 
                          sx={{ 
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            fontStyle: 'italic',
                            borderLeft: '3px solid #00f2ff',
                            pl: 1.5
                          }}
                        >
                          "{result.transcript}"
                        </Typography>
                      )}
                    </CardContent>
                    
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                        <Button
                            size="small"
                            color="inherit"
                            variant="outlined"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleViewMetadata(result);
                            }}
                            startIcon={<InfoIcon />}
                            sx={{ borderRadius: 2, borderColor: 'rgba(255,255,255,0.2)' }}
                        >
                            Info
                        </Button>
                        <Button
                            size="small"
                            color="secondary"
                            variant="outlined"
                            onClick={(e) => {
                                e.stopPropagation();
                                handleSummarize(result);
                            }}
                            startIcon={<SummarizeIcon />}
                            sx={{ borderRadius: 2 }}
                        >
                            Summarize
                        </Button>
                        <Button
                            size="small"
                            color="primary"
                            variant="contained"
                            onClick={() => window.open(`https://www.youtube.com/watch?v=${result.video_id || result.id}`, '_blank')}
                            startIcon={<PlayArrowIcon />}
                            sx={{ borderRadius: 2 }}
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
        <Box textAlign="center" py={10}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No results found
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ opacity: 0.6 }}>
            Try adjusting your search terms or selecting a different database.
          </Typography>
        </Box>
      )}

      {/* Summary Dialog */}
      <Dialog 
        open={summaryDialog.open} 
        onClose={handleCloseSummary}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#151a23', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' } }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" sx={{ color: '#ff0055', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
                <SummarizeIcon /> AI Summary
            </Typography>
            <IconButton onClick={handleCloseSummary} size="small" sx={{ color: 'text.secondary' }}>
              <CloseIcon />
            </IconButton>
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {summaryDialog.loading ? (
            <Box display="flex" justifyContent="center" my={4} flexDirection="column" alignItems="center">
              <CircularProgress color="secondary" />
              <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
                Analyzing video content...
              </Typography>
            </Box>
          ) : summaryDialog.error ? (
            <Alert severity="error" variant="filled">{summaryDialog.error}</Alert>
          ) : (
            <Box sx={{ color: '#e0e0e0', lineHeight: 1.8 }}>
                <ReactMarkdown>{summaryDialog.summary}</ReactMarkdown>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <Button onClick={handleCloseSummary} color="inherit">Close</Button>
        </DialogActions>
      </Dialog>

      {/* Metadata Dialog */}
      <Dialog 
        open={metadataDialog.open} 
        onClose={handleCloseMetadata}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#151a23', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' } }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="h6">Video Metadata</Typography>
          <IconButton onClick={handleCloseMetadata} size="small"><CloseIcon /></IconButton>
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {metadataDialog.loading ? (
            <Box display="flex" justifyContent="center" my={4}><CircularProgress /></Box>
          ) : metadataDialog.metadata ? (
            <Box>
              <Typography variant="subtitle1" gutterBottom sx={{ color: '#00f2ff' }}>
                {metadataDialog.metadata.title}
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, my: 2 }}>
                <Paper sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.03)' }}>
                    <Typography variant="caption" color="text.secondary">Channel</Typography>
                    <Typography variant="body2">{metadataDialog.metadata.channel}</Typography>
                </Paper>
                <Paper sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.03)' }}>
                    <Typography variant="caption" color="text.secondary">Views</Typography>
                    <Typography variant="body2">{parseInt(metadataDialog.metadata.view_count).toLocaleString()}</Typography>
                </Paper>
              </Box>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2, color: 'text.secondary' }}>
                Transcript Snippet:
              </Typography>
              <Box 
                sx={{ 
                  maxHeight: '200px', 
                  overflowY: 'auto', 
                  p: 2, 
                  bgcolor: 'rgba(0,0,0,0.3)',
                  borderRadius: 2,
                  border: '1px solid rgba(255,255,255,0.05)',
                  fontFamily: 'monospace',
                  fontSize: '0.85rem'
                }}
              >
                {metadataDialog.metadata.transcript || 'No transcript available'}
              </Box>
            </Box>
          ) : null}
        </DialogContent>
      </Dialog>
    </Container>
  );
}

export default SearchVideos;