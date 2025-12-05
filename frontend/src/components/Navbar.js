import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navButtonStyle = (path) => ({
    my: 2,
    mx: 1,
    color: isActive(path) ? '#00f2ff' : 'rgba(255,255,255,0.7)',
    display: 'flex',
    alignItems: 'center',
    gap: 1,
    position: 'relative',
    '&:hover': {
      color: '#fff',
      backgroundColor: 'rgba(255,255,255,0.05)',
    },
    '&::after': isActive(path) ? {
      content: '""',
      position: 'absolute',
      bottom: 0,
      left: '10%',
      width: '80%',
      height: '3px',
      borderRadius: '2px 2px 0 0',
      backgroundColor: '#00f2ff',
      boxShadow: '0 0 10px #00f2ff',
    } : {},
  });

  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters sx={{ height: 80 }}>
          <Box 
            component={RouterLink} 
            to="/"
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              textDecoration: 'none', 
              color: 'inherit',
              mr: 4 
            }}
          >
            <Box 
              sx={{ 
                p: 1, 
                borderRadius: '12px', 
                background: 'linear-gradient(135deg, #00f2ff 0%, #0061ff 100%)',
                display: 'flex',
                mr: 2,
                boxShadow: '0 0 15px rgba(0, 242, 255, 0.4)'
              }}
            >
              <VideoLibraryIcon sx={{ color: '#000' }} />
            </Box>
            <Typography
              variant="h5"
              noWrap
              sx={{
                fontFamily: 'Inter',
                fontWeight: 800,
                letterSpacing: '.05rem',
                background: 'linear-gradient(to right, #fff, #b0b8c4)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              QueryTube
            </Typography>
          </Box>

          <Box sx={{ flexGrow: 1, display: 'flex' }}>
            <Button
              component={RouterLink}
              to="/databases"
              sx={navButtonStyle('/databases')}
            >
              <StorageIcon fontSize="small" />
              Databases
            </Button>
            <Button
              component={RouterLink}
              to="/search"
              sx={navButtonStyle('/search')}
            >
              <SearchIcon fontSize="small" />
              Search
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

export default Navbar;