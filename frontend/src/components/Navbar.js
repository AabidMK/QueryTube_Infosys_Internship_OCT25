import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';

function Navbar() {
  return (
    <AppBar position="static">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <VideoLibraryIcon sx={{ display: 'flex', mr: 1 }} />
          <Typography
            variant="h6"
            noWrap
            component={RouterLink}
            to="/"
            sx={{
              mr: 2,
              display: 'flex',
              fontFamily: 'monospace',
              fontWeight: 700,
              letterSpacing: '.3rem',
              color: 'inherit',
              textDecoration: 'none',
            }}
          >
            QueryTube
          </Typography>

          <Box sx={{ flexGrow: 1, display: 'flex', ml: 3 }}>
            <Button
              component={RouterLink}
              to="/databases"
              sx={{ my: 2, color: 'white', display: 'block' }}
            >
              Databases
            </Button>
            <Button
              component={RouterLink}
              to="/search"
              sx={{ my: 2, color: 'white', display: 'block' }}
            >
              Search Videos
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Navbar;
