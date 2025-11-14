import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Container, Typography, Box, Paper, Grid } from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';

function Home() {
  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          my: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <Typography component="h1" variant="h3" gutterBottom>
          Welcome to QueryTube
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          A powerful video search and management system powered by ChromaDB
        </Typography>

        <Grid container spacing={4} sx={{ mt: 4 }}>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={3}
              sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}
            >
              <StorageIcon sx={{ fontSize: 60, mb: 2, alignSelf: 'center' }} />
              <Typography variant="h5" gutterBottom>
                Manage Databases
              </Typography>
              <Typography paragraph>
                Create, view, and manage your video databases. Upload new datasets and monitor your existing collections.
              </Typography>
              <Button
                variant="contained"
                component={Link}
                to="/databases"
                sx={{ mt: 'auto', alignSelf: 'center' }}
              >
                Go to Databases
              </Button>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper
              elevation={3}
              sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}
            >
              <SearchIcon sx={{ fontSize: 60, mb: 2, alignSelf: 'center' }} />
              <Typography variant="h5" gutterBottom>
                Search Videos
              </Typography>
              <Typography paragraph>
                Perform semantic search across your video collections. Find relevant content using natural language queries.
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                component={Link}
                to="/search"
                sx={{ mt: 'auto', alignSelf: 'center' }}
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
