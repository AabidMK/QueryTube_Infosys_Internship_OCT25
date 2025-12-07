import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Box,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  VideoLibrary,
  Person,
  Visibility,
  Schedule,
  ThumbUp,
  Comment,
  Refresh
} from '@mui/icons-material';
import { getStats, getHealthStatus, getSummarizerStatus } from '../services/api';

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [summarizerStatus, setSummarizerStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsData, healthData, summarizerData] = await Promise.all([
        getStats(),
        getHealthStatus(),
        getSummarizerStatus()
      ]);
      
      setStats(statsData);
      setHealth(healthData);
      setSummarizerStatus(summarizerData);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ py: 10, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ py: 3, mt: 8 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3, mt: 8 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1 }}>
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Overview of your YouTube video database and AI summarization system
          </Typography>
        </Box>
        
        <Chip 
          icon={<Refresh />}
          label="Last updated: Just now" 
          size="small"
          onClick={loadDashboardData}
        />
      </Box>

      {/* System Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, backgroundColor: '#212121' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <VideoLibrary /> Database Status
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <VideoLibrary color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Total Videos" 
                  secondary={stats?.total_videos || 0}
                />
                <Chip label="Active" color="success" size="small" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Person color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Unique Channels" 
                  secondary={stats?.unique_channels || 0}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Visibility color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Total Views" 
                  secondary={stats?.total_views?.toLocaleString() || 0}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <TrendingUp color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Average Views" 
                  secondary={stats?.average_views?.toLocaleString() || 0}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, backgroundColor: '#212121' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUp /> AI Summarizer Status
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  {summarizerStatus?.ai_available ? (
                    <ThumbUp color="success" />
                  ) : (
                    <ThumbUp color="error" />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary="AI Availability" 
                  secondary={summarizerStatus?.ai_available ? 'Available' : 'Unavailable'}
                />
                <Chip 
                  label={summarizerStatus?.ai_available ? "Active" : "Inactive"} 
                  color={summarizerStatus?.ai_available ? "success" : "error"} 
                  size="small" 
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Schedule color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Model" 
                  secondary={summarizerStatus?.model || 'llama3.2'}
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Comment color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Status" 
                  secondary={summarizerStatus?.status || 'Unknown'}
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Top Channels */}
      {stats?.top_channels && Object.keys(stats.top_channels).length > 0 && (
        <Paper sx={{ p: 3, mb: 4, backgroundColor: '#212121' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Top Channels by Video Count
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(stats.top_channels).map(([channel, count], index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={channel}>
                <Card sx={{ backgroundColor: '#1C1C1C' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2" noWrap sx={{ maxWidth: '70%' }}>
                        {index + 1}. {channel}
                      </Typography>
                      <Chip label={count} size="small" color="primary" />
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={(count / stats.total_videos) * 100}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Health Status */}
      <Paper sx={{ p: 3, backgroundColor: '#212121' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          System Health
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1C1C1C' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  API Status
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    {health?.status === 'healthy' ? '✅ Healthy' : '❌ Unhealthy'}
                  </Typography>
                  <Chip 
                    label={health?.status || 'Unknown'} 
                    color={health?.status === 'healthy' ? 'success' : 'error'} 
                    size="small" 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1C1C1C' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Database Connection
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    {health?.database === 'connected' ? '✅ Connected' : '❌ Disconnected'}
                  </Typography>
                  <Chip 
                    label={health?.database || 'Unknown'} 
                    color={health?.database === 'connected' ? 'success' : 'error'} 
                    size="small" 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ backgroundColor: '#1C1C1C' }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Summarizer Status
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2">
                    {summarizerStatus?.status === 'available' ? '✅ Available' : '❌ Unavailable'}
                  </Typography>
                  <Chip 
                    label={summarizerStatus?.status || 'Unknown'} 
                    color={summarizerStatus?.status === 'available' ? 'success' : 'error'} 
                    size="small" 
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default DashboardPage;