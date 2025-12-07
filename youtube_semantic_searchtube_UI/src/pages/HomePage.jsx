import React from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  Paper
} from '@mui/material';
import {
  Search,
  TrendingUp,
  Summarize,
  YouTube
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Semantic Search',
      description: 'Search through 615+ videos using AI-powered semantic search',
      icon: <Search sx={{ fontSize: 40, color: '#FF0000' }} />,
      color: 'linear-gradient(135deg, #FF0000, #FF6B6B)'
    },
    {
      title: 'AI Summarization',
      description: 'Get instant summaries of YouTube videos using Ollama AI',
      icon: <Summarize sx={{ fontSize: 40, color: '#00D100' }} />,
      color: 'linear-gradient(135deg, #00D100, #6BFF6B)'
    },
    {
      title: 'Video Analytics',
      description: 'View statistics, metadata, and insights for each video',
      icon: <TrendingUp sx={{ fontSize: 40, color: '#FFD600' }} />,
      color: 'linear-gradient(135deg, #FFD600, #FFF46B)'
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3, mt: 8 }}>
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <YouTube sx={{ fontSize: 80, color: '#FF0000', mb: 2 }} />
        <Typography 
          variant="h2" 
          sx={{ 
            mb: 2,
            fontWeight: 800,
            background: 'linear-gradient(45deg, #FF0000, #FF6B6B)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          YouTube Semantic Search
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          AI-powered search and summarization for YouTube videos
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mb: 6 }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<Search />}
            onClick={() => navigate('/search')}
            sx={{
              backgroundColor: '#FF0000',
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              '&:hover': {
                backgroundColor: '#CC0000'
              }
            }}
          >
            Start Searching
          </Button>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Summarize />}
            onClick={() => navigate('/summarize')}
            sx={{
              borderColor: '#FF0000',
              color: '#FF0000',
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              '&:hover': {
                borderColor: '#CC0000',
                backgroundColor: 'rgba(255, 0, 0, 0.1)'
              }
            }}
          >
            Try Summarizer
          </Button>
        </Box>

        <Chip 
          label="615+ Videos Indexed • AI-Powered • Real-time Search" 
          sx={{ 
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            color: '#FF0000',
            fontSize: '0.9rem',
            py: 2
          }}
        />
      </Box>

      {/* Features Grid */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                background: feature.color,
                backgroundImage: 'none',
                transition: 'transform 0.3s',
                '&:hover': {
                  transform: 'translateY(-8px)'
                }
              }}
            >
              <CardContent sx={{ p: 3, color: 'white' }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Stats */}
      <Paper sx={{ p: 3, backgroundColor: '#212121', mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 3 }}>
          Quick Stats
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="primary">
                615
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Videos Indexed
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="success.main">
                100%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI Summarization
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="warning.main">
                0.2s
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg. Search Time
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h3" color="error.main">
                24/7
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Availability
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default HomePage;