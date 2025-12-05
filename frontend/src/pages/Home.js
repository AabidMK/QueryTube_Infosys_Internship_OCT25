import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Container, Typography, Box, Paper, Grid } from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

function Home() {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          minHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
        }}
        className="fade-in"
      >
        <Box sx={{ mb: 6, maxWidth: '800px' }}>
          <Typography 
            component="h1" 
            variant="h2" 
            gutterBottom
            sx={{ 
              background: 'linear-gradient(45deg, #00f2ff 10%, #ffffff 90%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 800,
              mb: 2,
              filter: 'drop-shadow(0 0 20px rgba(0, 242, 255, 0.2))'
            }}
          >
            Welcome to QueryTube
          </Typography>
          <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 300, lineHeight: 1.6 }}>
            The next generation video search and management system powered by 
            <Box component="span" sx={{ color: '#ff0055', fontWeight: 600, mx: 1 }}>ChromaDB</Box>
            Semantic Search.
          </Typography>
        </Box>

        <Grid container spacing={4} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{ 
                p: 5, 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: '24px',
                border: '1px solid rgba(255,255,255,0.08)',
                background: 'linear-gradient(180deg, rgba(21, 26, 35, 0.6) 0%, rgba(11, 14, 20, 0.8) 100%)',
              }}
            >
              <Box 
                sx={{ 
                  width: 80, 
                  height: 80, 
                  borderRadius: '20px', 
                  bgcolor: 'rgba(0, 242, 255, 0.1)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  mb: 3,
                  alignSelf: 'center',
                  color: '#00f2ff'
                }}
              >
                <StorageIcon sx={{ fontSize: 40 }} />
              </Box>
              <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 700 }}>
                Manage Databases
              </Typography>
              <Typography paragraph color="text.secondary" align="center" sx={{ flexGrow: 1, mb: 4 }}>
                Create, view, and manage your video databases. Upload new datasets via CSV and monitor your existing collections with real-time stats.
              </Typography>
              <Button
                variant="outlined"
                size="large"
                component={Link}
                to="/databases"
                endIcon={<ArrowForwardIcon />}
                sx={{ 
                  mt: 'auto', 
                  borderColor: 'rgba(0, 242, 255, 0.5)', 
                  color: '#00f2ff',
                  borderWidth: 2,
                  '&:hover': { borderWidth: 2, borderColor: '#00f2ff', bgcolor: 'rgba(0, 242, 255, 0.1)' }
                }}
              >
                Manage Data
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{ 
                p: 5, 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: '24px',
                border: '1px solid rgba(255,255,255,0.08)',
                background: 'linear-gradient(180deg, rgba(21, 26, 35, 0.6) 0%, rgba(11, 14, 20, 0.8) 100%)',
              }}
            >
              <Box 
                sx={{ 
                  width: 80, 
                  height: 80, 
                  borderRadius: '20px', 
                  bgcolor: 'rgba(255, 0, 85, 0.1)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  mb: 3,
                  alignSelf: 'center',
                  color: '#ff0055'
                }}
              >
                <SearchIcon sx={{ fontSize: 40 }} />
              </Box>
              <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 700 }}>
                Semantic Search
              </Typography>
              <Typography paragraph color="text.secondary" align="center" sx={{ flexGrow: 1, mb: 4 }}>
                Perform deep semantic search across your video collections. Find exactly what you need using natural language queries and AI summarization.
              </Typography>
              <Button
                variant="contained"
                size="large"
                color="secondary"
                component={Link}
                to="/search"
                endIcon={<ArrowForwardIcon />}
                sx={{ mt: 'auto', boxShadow: '0 4px 20px rgba(255, 0, 85, 0.4)' }}
              >
                Start Searching
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}

export default Home;