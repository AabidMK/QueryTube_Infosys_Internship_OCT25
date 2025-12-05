import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import DatabaseManager from './pages/DatabaseManager';
import SearchVideos from './pages/SearchVideos';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0b0e14',
      paper: '#151a23',
    },
    primary: {
      main: '#00f2ff',
      contrastText: '#000',
    },
    secondary: {
      main: '#ff0055',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0b8c4',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h3: { fontWeight: 800 },
    h4: { fontWeight: 700 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  shape: { borderRadius: 16 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: "#2b3342 #0b0e14",
          "&::-webkit-scrollbar, & *::-webkit-scrollbar": { backgroundColor: "#0b0e14", width: "8px" },
          "&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb": { borderRadius: 8, backgroundColor: "#2b3342", minHeight: 24, border: "2px solid #0b0e14" },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(11, 14, 20, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          boxShadow: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 50, padding: '10px 24px', boxShadow: 'none' },
        containedPrimary: { background: 'linear-gradient(45deg, #00f2ff 30%, #00c8ff 90%)', color: '#000' },
        containedSecondary: { background: 'linear-gradient(45deg, #ff0055 30%, #ff0088 90%)' },
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
            // Subtle global background
            backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(0, 242, 255, 0.05) 0%, rgba(11, 14, 20, 0) 50%)'
          }}
        >
          <Navbar />
          {/* REMOVED 'p: 3' HERE. This allows Home.js to touch the edges. */}
          <Box component="main" sx={{ flexGrow: 1, width: '100%' }}>
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