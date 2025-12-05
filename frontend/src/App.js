import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import DatabaseManager from './pages/DatabaseManager';
import SearchVideos from './pages/SearchVideos';

// Create a custom "Cyber-Dark" theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0b0e14', // Very deep navy/black
      paper: '#151a23',   // Slightly lighter for cards
    },
    primary: {
      main: '#00f2ff', // Neon Cyan
      contrastText: '#000',
    },
    secondary: {
      main: '#ff0055', // Neon Pink/Magenta
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b8c4',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h3: {
      fontWeight: 800,
      letterSpacing: '-0.02em',
    },
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none', // Remove all caps
    },
  },
  shape: {
    borderRadius: 16, // Softer corners
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: "#2b3342 #0b0e14",
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": {
            backgroundColor: "#0b0e14",
            width: "8px",
          },
          "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": {
            borderRadius: 8,
            backgroundColor: "#2b3342",
            minHeight: 24,
            border: "2px solid #0b0e14",
          },
          "&::-webkit-scrollbar-thumb:focus, & *::-webkit-scrollbar-thumb:focus": {
            backgroundColor: "#00f2ff",
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(11, 14, 20, 0.8)', // Glass effect
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          boxShadow: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(21, 26, 35, 0.6)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out, border-color 0.3s',
          '&:hover': {
            transform: 'translateY(-5px)',
            boxShadow: '0 10px 30px -10px rgba(0, 242, 255, 0.15)',
            borderColor: 'rgba(0, 242, 255, 0.3)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 50, // Pill shape
          padding: '10px 24px',
          boxShadow: 'none',
          transition: 'all 0.2s',
          '&:hover': {
            boxShadow: '0 0 15px rgba(0, 242, 255, 0.3)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(45deg, #00f2ff 30%, #00c8ff 90%)',
          color: '#000',
        },
        containedSecondary: {
          background: 'linear-gradient(45deg, #ff0055 30%, #ff0088 90%)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none', // Remove default material overlay
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: 12,
            '& fieldset': {
              borderColor: 'rgba(255,255,255,0.1)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(255,255,255,0.3)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00f2ff',
            },
          },
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            minHeight: '100vh',
            backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(0, 242, 255, 0.05) 0%, rgba(11, 14, 20, 0) 50%)'
          }}
        >
          <Navbar />
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/databases" element={<DatabaseManager />} />
              <Route path="/search" element={<SearchVideos />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;