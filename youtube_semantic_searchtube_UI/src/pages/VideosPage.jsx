import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  TextField,
  MenuItem,
  Pagination,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import {
  FilterList,
  Sort,
  GridView,
  ViewList
} from '@mui/icons-material';
import VideoCard from '../components/Video/VideoCard';
import EmptyState from '../components/Common/EmptyState';
import { listVideos } from '../services/api';

const VideosPage = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalVideos, setTotalVideos] = useState(0);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filters, setFilters] = useState({
    sortBy: 'date',
    limit: 12
  });

  useEffect(() => {
    loadVideos();
  }, [page, filters]);

  const loadVideos = async () => {
    setLoading(true);
    try {
      const offset = (page - 1) * filters.limit;
      const response = await listVideos(filters.limit, offset);
      
      setVideos(response.videos);
      setTotalVideos(response.total_videos);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load videos');
      console.error('Load videos error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = (videoId) => {
    console.log('Summarize video:', videoId);
    // Implement summarization logic
  };

  const handleOpenVideo = (videoId) => {
    window.open(`https://youtube.com/watch?v=${videoId}`, '_blank');
  };

  const totalPages = Math.ceil(totalVideos / filters.limit);

  if (loading && videos.length === 0) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3, mt: 8 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1 }}>
            All Videos
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Browse through {totalVideos} indexed YouTube videos
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {/* View Toggle */}
          <Box sx={{ display: 'flex', border: '1px solid #333', borderRadius: 1 }}>
            <Chip
              icon={<GridView />}
              label="Grid"
              onClick={() => setViewMode('grid')}
              sx={{
                borderRadius: 1,
                backgroundColor: viewMode === 'grid' ? '#FF0000' : 'transparent',
                color: viewMode === 'grid' ? 'white' : 'inherit'
              }}
            />
            <Chip
              icon={<ViewList />}
              label="List"
              onClick={() => setViewMode('list')}
              sx={{
                borderRadius: 1,
                backgroundColor: viewMode === 'list' ? '#FF0000' : 'transparent',
                color: viewMode === 'list' ? 'white' : 'inherit'
              }}
            />
          </Box>

          {/* Filters */}
          <TextField
            select
            size="small"
            label="Sort by"
            value={filters.sortBy}
            onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="date">Date Added</MenuItem>
            <MenuItem value="views">Views</MenuItem>
            <MenuItem value="title">Title</MenuItem>
            <MenuItem value="channel">Channel</MenuItem>
          </TextField>

          <TextField
            select
            size="small"
            label="Show"
            value={filters.limit}
            onChange={(e) => setFilters({...filters, limit: parseInt(e.target.value)})}
            sx={{ minWidth: 120 }}
          >
            <MenuItem value={12}>12 per page</MenuItem>
            <MenuItem value={24}>24 per page</MenuItem>
            <MenuItem value={48}>48 per page</MenuItem>
          </TextField>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Videos Grid/List */}
      {videos.length > 0 ? (
        <>
          <Grid container spacing={3}>
            {videos.map((video) => (
              <Grid 
                item 
                key={video.video_id} 
                xs={viewMode === 'grid' ? 12 : 12}
                sm={viewMode === 'grid' ? 6 : 12}
                md={viewMode === 'grid' ? 4 : 12}
                lg={viewMode === 'grid' ? 3 : 12}
              >
                <VideoCard
                  video={video}
                  onSummarize={handleSummarize}
                  onOpenVideo={handleOpenVideo}
                  compact={viewMode === 'list'}
                />
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination 
                count={totalPages} 
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
                sx={{
                  '& .MuiPaginationItem-root': {
                    color: 'white'
                  }
                }}
              />
            </Box>
          )}
        </>
      ) : (
        <EmptyState
          title="No Videos Found"
          description="No videos are currently indexed in the database."
          icon="youtube"
        />
      )}
    </Container>
  );
};

export default VideosPage;