import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  Chip,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  TextField,
  MenuItem,
  Pagination,
  Button  // ADD THIS IMPORT
} from '@mui/material';
import {
  FilterList,
  Sort,
  Refresh,
  Download
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import SearchBar from '../components/Search/SearchBar';
import VideoCard from '../components/Video/VideoCard';
import EmptyState from '../components/Common/EmptyState';
import { searchVideos, searchVideosWithSummary, getHealthStatus } from '../services/api';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recentSearches, setRecentSearches] = useState([]);
  const [apiStatus, setApiStatus] = useState(null);
  const [apiLoading, setApiLoading] = useState(true);
  const [filters, setFilters] = useState({
    channel: '',
    sortBy: 'relevance',
    includeSummary: false,
    resultsCount: 10
  });

  const channelOptions = [
    'BRIGHT SIDE',
    'Kurzgesagt',
    'Veritasium',
    'Vsauce',
    'Mark Rober'
  ];

  useEffect(() => {
    // Load recent searches from localStorage
    const savedSearches = JSON.parse(localStorage.getItem('recentSearches')) || [];
    setRecentSearches(savedSearches);
    
    // Check API status
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      const health = await getHealthStatus();
      setApiStatus(health);
      setApiLoading(false);
    } catch (error) {
      console.error('API not reachable:', error);
      setApiStatus(null);
      setApiLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    console.log('🔍 Starting search for:', query);
    
    try {
      // First check API status
      await checkApiStatus();
      
      if (!apiStatus || apiStatus.status !== 'healthy') {
        throw new Error('API server is not available. Please start the FastAPI server on port 8000.');
      }

      // Use regular search (more reliable)
      const response = await searchVideos(
        query,
        filters.resultsCount,
        filters.channel || null
      );

      console.log('✅ Search results:', response);
      
      if (response.results_count === 0) {
        setError(`No videos found for "${query}". Try different keywords.`);
        setSearchResults([]);
      } else {
        setSearchResults(response.results);
        setSearchQuery(query);

        // Save to recent searches
        const updatedSearches = [
          query,
          ...recentSearches.filter(s => s !== query)
        ].slice(0, 5);
        
        setRecentSearches(updatedSearches);
        localStorage.setItem('recentSearches', JSON.stringify(updatedSearches));
      }
    } catch (err) {
      console.error('❌ Search error:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummarize = (videoId) => {
    console.log('Summarize video:', videoId);
    // Navigate to summary page
    window.location.href = `/summarize?video_id=${videoId}`;
  };

  const handleOpenVideo = (videoId) => {
    window.open(`https://youtube.com/watch?v=${videoId}`, '_blank');
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3, mt: 8 }}>
      {/* API Status Banner */}
      {!apiLoading && !apiStatus && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button 
              color="inherit" 
              size="small" 
              onClick={checkApiStatus}
            >
              Retry
            </Button>
          }
        >
          ⚠️ API server is not reachable. Please make sure:
          <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
            <li>FastAPI server is running on port 8000</li>
            <li>CORS is enabled in the FastAPI app</li>
            <li>No firewall is blocking the connection</li>
          </ul>
          <Button 
            variant="contained" 
            size="small" 
            sx={{ mt: 1 }}
            onClick={() => window.open('http://localhost:8000/docs', '_blank')}
          >
            Open API Documentation
          </Button>
        </Alert>
      )}

      {/* Search Header */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            mb: 2,
            fontWeight: 700,
            background: 'linear-gradient(45deg, #FF0000, #FF6B6B)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          YouTube Semantic Search
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Search through 615+ videos with AI-powered semantic search and summarization
        </Typography>

        <SearchBar
          onSearch={handleSearch}
          isLoading={isLoading}
          recentSearches={recentSearches}
          onRecentSearchClick={handleSearch}
        />
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3, backgroundColor: '#212121' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterList />
            <Typography variant="body2">Filters</Typography>
          </Box>

          <TextField
            select
            size="small"
            label="Channel"
            value={filters.channel}
            onChange={(e) => handleFilterChange('channel', e.target.value)}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="">All Channels</MenuItem>
            {channelOptions.map((channel) => (
              <MenuItem key={channel} value={channel}>
                {channel}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            size="small"
            label="Sort by"
            value={filters.sortBy}
            onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="relevance">Relevance</MenuItem>
            <MenuItem value="views">Views</MenuItem>
            <MenuItem value="date">Date</MenuItem>
            <MenuItem value="similarity">Similarity</MenuItem>
          </TextField>

          <TextField
            select
            size="small"
            label="Results"
            value={filters.resultsCount}
            onChange={(e) => handleFilterChange('resultsCount', e.target.value)}
            sx={{ minWidth: 120 }}
          >
            <MenuItem value={5}>5 results</MenuItem>
            <MenuItem value={10}>10 results</MenuItem>
            <MenuItem value={20}>20 results</MenuItem>
            <MenuItem value={50}>50 results</MenuItem>
          </TextField>

          <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
            <Tooltip title="Refresh">
              <IconButton onClick={() => handleSearch(searchQuery)}>
                <Refresh />
              </IconButton>
            </Tooltip>

            <Tooltip title="Export Results">
              <IconButton>
                <Download />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results Count */}
      {searchResults.length > 0 && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            Found {searchResults.length} videos for "{searchQuery}"
          </Typography>
          <Chip 
            label={`Similarity Score: High → Low`} 
            sx={{ backgroundColor: 'primary.main', color: 'white' }}
          />
        </Box>
      )}

      {/* Loading State */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
          <CircularProgress />
        </Box>
      ) : (
        <AnimatePresence>
          {/* Results Grid */}
          {searchResults.length > 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Grid container spacing={3}>
                {searchResults.map((video, index) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={video.video_id || index}>
                    <VideoCard
                      video={video}
                      onSummarize={handleSummarize}
                      onOpenVideo={handleOpenVideo}
                    />
                  </Grid>
                ))}
              </Grid>

              {/* Pagination */}
              {searchResults.length > 10 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <Pagination 
                    count={Math.ceil(searchResults.length / 10)} 
                    color="primary" 
                    sx={{
                      '& .MuiPaginationItem-root': {
                        color: 'white'
                      }
                    }}
                  />
                </Box>
              )}
            </motion.div>
          ) : (
            /* Empty State */
            !isLoading && searchQuery && (
              <EmptyState
                title="No results found"
                description={`No videos found for "${searchQuery}". Try different keywords.`}
                icon="search"
              />
            )
          )}
        </AnimatePresence>
      )}

      {/* Initial State */}
      {!isLoading && searchResults.length === 0 && !searchQuery && (
        <EmptyState
          title="YouTube Semantic Search"
          description="Search through 615+ videos with AI-powered semantic search. Enter keywords to find relevant videos."
          icon="youtube"
        />
      )}
    </Container>
  );
};

export default SearchPage;