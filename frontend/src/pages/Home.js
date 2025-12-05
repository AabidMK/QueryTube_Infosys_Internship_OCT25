import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Typography, Box, Paper, useTheme, useMediaQuery } from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import SearchIcon from '@mui/icons-material/Search';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

function Home() {
  const theme = useTheme();
  // On mobile (md and down), stack vertically. On desktop, split horizontally.
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box 
      className="fade-in"
      sx={{ 
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        width: '100%', 
        height: 'calc(100vh - 80px)', // Exactly fills remaining screen height (Navbar is 80px)
        overflow: 'hidden',
        position: 'relative'
      }} 
    >
      
      {/* Background Text - Fixed Position to ensure perfect center */}
      {!isMobile && (
        <Box 
          sx={{ 
            position: 'absolute', 
            top: '50%', 
            left: '50%', 
            transform: 'translate(-50%, -50%)',
            pointerEvents: 'none',
            zIndex: 0,
            opacity: 0.05,
            userSelect: 'none',
            whiteSpace: 'nowrap'
          }}
        >
          <Typography 
            variant="h1" 
            sx={{ 
              fontWeight: 900, 
              fontSize: '25rem', 
              color: '#fff',
              letterSpacing: '-2rem',
              lineHeight: 0.8
            }}
          >
            QT
          </Typography>
        </Box>
      )}

      {/* LEFT SIDE - DATABASES */}
      <Box 
        sx={{ 
          width: isMobile ? '100%' : '50%', // EXACTLY 50% width
          height: isMobile ? '50%' : '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          p: 4,
          borderRight: isMobile ? 'none' : '1px solid rgba(255, 255, 255, 0.05)',
          borderBottom: isMobile ? '1px solid rgba(255, 255, 255, 0.05)' : 'none',
          // Subtle Cyan Gradient on Left
          background: 'linear-gradient(90deg, transparent 0%, rgba(0, 242, 255, 0.03) 100%)',
          position: 'relative',
          zIndex: 1,
          transition: 'all 0.4s ease',
          '&:hover': {
            background: 'linear-gradient(90deg, transparent 0%, rgba(0, 242, 255, 0.08) 100%)',
            '& .icon-glow': { transform: 'scale(1.1)', boxShadow: '0 0 50px rgba(0, 242, 255, 0.3)' }
          }
        }}
      >
        <Paper
          elevation={0}
          className="icon-glow"
          sx={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            bgcolor: 'rgba(0, 242, 255, 0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 4,
            border: '1px solid rgba(0, 242, 255, 0.2)',
            transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
          }}
        >
          <StorageIcon sx={{ fontSize: 60, color: '#00f2ff' }} />
        </Paper>

        <Typography variant="h3" gutterBottom sx={{ color: '#fff' }}>
          Databases
        </Typography>
        
        <Typography variant="h6" sx={{ color: 'text.secondary', mb: 5, maxWidth: 400, fontWeight: 300 }}>
          Ingest and manage your video collections.
        </Typography>

        <Button
          component={Link}
          to="/databases"
          variant="outlined"
          size="large"
          endIcon={<ArrowForwardIcon />}
          sx={{
            borderColor: '#00f2ff',
            color: '#00f2ff',
            borderWidth: 2,
            px: 5,
            py: 1.5,
            fontSize: '1.1rem',
            '&:hover': {
              borderWidth: 2,
              borderColor: '#00f2ff',
              bgcolor: 'rgba(0, 242, 255, 0.1)',
              boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)'
            }
          }}
        >
          Manage Data
        </Button>
      </Box>

      {/* RIGHT SIDE - SEARCH */}
      <Box 
        sx={{ 
          width: isMobile ? '100%' : '50%', // EXACTLY 50% width
          height: isMobile ? '50%' : '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          p: 4,
          // Subtle Pink Gradient on Right
          background: 'linear-gradient(270deg, transparent 0%, rgba(255, 0, 85, 0.03) 100%)',
          position: 'relative',
          zIndex: 1,
          transition: 'all 0.4s ease',
          '&:hover': {
            background: 'linear-gradient(270deg, transparent 0%, rgba(255, 0, 85, 0.08) 100%)',
            '& .icon-glow': { transform: 'scale(1.1)', boxShadow: '0 0 50px rgba(255, 0, 85, 0.3)' }
          }
        }}
      >
        <Paper
          elevation={0}
          className="icon-glow"
          sx={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            bgcolor: 'rgba(255, 0, 85, 0.05)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            mb: 4,
            border: '1px solid rgba(255, 0, 85, 0.2)',
            transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
          }}
        >
          <SearchIcon sx={{ fontSize: 60, color: '#ff0055' }} />
        </Paper>

        <Typography variant="h3" gutterBottom sx={{ color: '#fff' }}>
          Search
        </Typography>
        
        <Typography variant="h6" sx={{ color: 'text.secondary', mb: 5, maxWidth: 400, fontWeight: 300 }}>
          Find content using semantic AI queries.
        </Typography>

        <Button
          component={Link}
          to="/search"
          variant="contained"
          color="secondary"
          size="large"
          endIcon={<ArrowForwardIcon />}
          sx={{
            px: 6,
            py: 1.5,
            fontSize: '1.1rem',
            boxShadow: '0 4px 20px rgba(255, 0, 85, 0.25)',
            '&:hover': {
              boxShadow: '0 4px 30px rgba(255, 0, 85, 0.5)'
            }
          }}
        >
          Start Searching
        </Button>
      </Box>

    </Box>
  );
}

export default Home;