import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Button,
  Collapse
} from '@mui/material';
import {
  PlayCircle,
  Summarize,
  OpenInNew,
  ThumbUp,
  Visibility,
  Schedule,
  ExpandMore,
  ExpandLess,
  Description
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { formatNumber, formatDuration, getSimilarityColor, truncateText } from '../../utils/formatters';

const VideoCard = ({ video, onSummarize, onOpenVideo, compact = false }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Safely get thumbnail URL
  const getThumbnailUrl = () => {
    if (!video || !video.video_id) return '';
    return `https://img.youtube.com/vi/${video.video_id}/hqdefault.jpg`;
  };
  
  const thumbnailUrl = getThumbnailUrl();
  
  // Handle missing video data
  if (!video) {
    return (
      <Card sx={{ p: 3, textAlign: 'center', backgroundColor: '#212121' }}>
        <Typography color="text.secondary">No video data available</Typography>
      </Card>
    );
  }

  // Compact view for list display
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card 
          sx={{ 
            display: 'flex', 
            mb: 2,
            transition: 'transform 0.2s, box-shadow 0.2s',
            '&:hover': {
              transform: 'translateX(4px)',
              boxShadow: '0 4px 12px rgba(255, 0, 0, 0.2)',
            }
          }}
        >
          {/* Thumbnail */}
          <Box sx={{ position: 'relative', minWidth: 160 }}>
            <CardMedia
              component="img"
              sx={{ width: 160, height: 90 }}
              image={thumbnailUrl}
              alt={video.title || 'Video thumbnail'}
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/160x90/212121/666666?text=No+Thumbnail';
              }}
            />
            
            {/* Duration Badge */}
            {video.duration && (
              <Chip
                label={formatDuration(video.duration)}
                size="small"
                sx={{
                  position: 'absolute',
                  bottom: 4,
                  right: 4,
                  backgroundColor: 'rgba(0, 0, 0, 0.8)',
                  color: 'white',
                  fontSize: '0.7rem'
                }}
              />
            )}
          </Box>

          <CardContent sx={{ flex: 1, p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              {/* Title and Channel */}
              <Box sx={{ flex: 1 }}>
                <Typography 
                  variant="subtitle1" 
                  sx={{ 
                    fontWeight: 600,
                    mb: 0.5,
                    display: '-webkit-box',
                    WebkitLineClamp: 1,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {video.title || 'Untitled Video'}
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary"
                  sx={{ mb: 1 }}
                >
                  {video.channel || 'Unknown Channel'}
                </Typography>
              </Box>

              {/* Similarity Score */}
              {video.similarity_score !== undefined && (
                <Box sx={{ ml: 2 }}>
                  <Tooltip title={`Similarity: ${(video.similarity_score * 100).toFixed(1)}%`}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={video.similarity_score * 100}
                        sx={{ 
                          width: 60,
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: '#333',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: getSimilarityColor(video.similarity_score)
                          }
                        }}
                      />
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          ml: 1, 
                          fontWeight: 'bold',
                          color: getSimilarityColor(video.similarity_score)
                        }}
                      >
                        {video.similarity_score.toFixed(2)}
                      </Typography>
                    </Box>
                  </Tooltip>
                </Box>
              )}
            </Box>

            {/* Stats */}
            <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
              {video.views && (
                <Typography variant="caption" color="text.secondary">
                  👁️ {formatNumber(video.views)}
                </Typography>
              )}
              {video.duration && (
                <Typography variant="caption" color="text.secondary">
                  ⏱️ {formatDuration(video.duration)}
                </Typography>
              )}
              {video.published_at && (
                <Typography variant="caption" color="text.secondary">
                  📅 {new Date(video.published_at).toLocaleDateString()}
                </Typography>
              )}
            </Box>

            {/* Content Preview */}
            {video.content_preview && (
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ 
                  fontSize: '0.8rem',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden'
                }}
              >
                {video.content_preview}
              </Typography>
            )}
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  // Original grid view
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          transition: 'transform 0.2s, box-shadow 0.2s',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 24px rgba(255, 0, 0, 0.2)',
          }
        }}
      >
        {/* Thumbnail */}
        <Box sx={{ position: 'relative' }}>
          <CardMedia
            component="img"
            height="180"
            image={thumbnailUrl}
            alt={video.title || 'Video thumbnail'}
            sx={{ objectFit: 'cover' }}
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/320x180/212121/666666?text=No+Thumbnail';
            }}
          />
          
          {/* Duration Badge */}
          {video.duration && (
            <Chip
              label={formatDuration(video.duration)}
              size="small"
              sx={{
                position: 'absolute',
                bottom: 8,
                right: 8,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                color: 'white',
                fontSize: '0.75rem'
              }}
            />
          )}

          {/* Similarity Score */}
          {video.similarity_score !== undefined && (
            <Box sx={{ position: 'absolute', top: 8, left: 8 }}>
              <Tooltip title={`Similarity: ${(video.similarity_score * 100).toFixed(1)}%`}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={video.similarity_score * 100}
                    sx={{ 
                      width: 60,
                      height: 6,
                      borderRadius: 3,
                      backgroundColor: '#333',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getSimilarityColor(video.similarity_score)
                      }
                    }}
                  />
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      ml: 1, 
                      color: 'white',
                      fontWeight: 'bold',
                      textShadow: '0 1px 2px rgba(0,0,0,0.8)'
                    }}
                  >
                    {video.similarity_score.toFixed(2)}
                  </Typography>
                </Box>
              </Tooltip>
            </Box>
          )}

          {/* Play Button Overlay */}
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              opacity: 0,
              transition: 'opacity 0.2s',
              '&:hover': {
                opacity: 1
              }
            }}
          >
            <IconButton 
              onClick={() => video.video_id && onOpenVideo(video.video_id)}
              sx={{ 
                backgroundColor: 'rgba(255, 0, 0, 0.9)',
                '&:hover': {
                  backgroundColor: '#FF0000'
                }
              }}
            >
              <PlayCircle sx={{ fontSize: 48, color: 'white' }} />
            </IconButton>
          </Box>
        </Box>

        <CardContent sx={{ flexGrow: 1, p: 2 }}>
          {/* Title */}
          <Typography 
            variant="subtitle1" 
            sx={{ 
              fontWeight: 600,
              mb: 1,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              minHeight: '3em'
            }}
          >
            {video.title || 'Untitled Video'}
          </Typography>

          {/* Channel */}
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ mb: 1 }}
          >
            {video.channel || 'Unknown Channel'}
          </Typography>

          {/* Stats Row */}
          <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
            {video.views && (
              <Tooltip title="Views">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Visibility sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption">
                    {formatNumber(video.views)}
                  </Typography>
                </Box>
              </Tooltip>
            )}

            {video.duration && (
              <Tooltip title="Duration">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption">
                    {formatDuration(video.duration)}
                  </Typography>
                </Box>
              </Tooltip>
            )}

            {video.published_at && (
              <Tooltip title="Published Date">
                <Typography variant="caption" color="text.secondary">
                  {new Date(video.published_at).toLocaleDateString()}
                </Typography>
              </Tooltip>
            )}
          </Box>

          {/* Content Preview */}
          {video.content_preview && (
            <>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ 
                  fontSize: '0.8rem',
                  mb: 1,
                  display: '-webkit-box',
                  WebkitLineClamp: expanded ? 10 : 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  minHeight: expanded ? 'auto' : '2.4em'
                }}
              >
                {video.content_preview}
              </Typography>
              
              <Button
                size="small"
                onClick={() => setExpanded(!expanded)}
                sx={{
                  color: 'primary.main',
                  textTransform: 'none',
                  p: 0,
                  minWidth: 'auto',
                  '&:hover': { 
                    backgroundColor: 'transparent',
                    textDecoration: 'underline'
                  }
                }}
                startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              >
                {expanded ? 'Show Less' : 'Show More'}
              </Button>
            </>
          )}

          {/* Tags */}
          {video.tags && (
            <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {typeof video.tags === 'string' 
                ? video.tags.split(',').slice(0, 3).map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag.trim()}
                      size="small"
                      sx={{
                        fontSize: '0.65rem',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      }}
                    />
                  ))
                : null}
            </Box>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
            <Tooltip title="Summarize Video">
              <IconButton 
                size="small" 
                onClick={() => video.video_id && onSummarize(video.video_id)}
                sx={{ 
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark'
                  }
                }}
              >
                <Summarize sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>

            <Tooltip title="Open on YouTube">
              <IconButton 
                size="small" 
                onClick={() => video.video_id && window.open(`https://youtube.com/watch?v=${video.video_id}`, '_blank')}
                sx={{ 
                  backgroundColor: 'secondary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'secondary.dark'
                  }
                }}
              >
                <OpenInNew sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>

            {video.video_id && (
              <Tooltip title="View Details">
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<Description />}
                  onClick={() => window.location.href = `/videos/${video.video_id}`}
                  sx={{ 
                    ml: 'auto',
                    borderColor: 'rgba(255, 255, 255, 0.23)',
                    color: 'text.secondary',
                    fontSize: '0.75rem'
                  }}
                >
                  Details
                </Button>
              </Tooltip>
            )}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default VideoCard;