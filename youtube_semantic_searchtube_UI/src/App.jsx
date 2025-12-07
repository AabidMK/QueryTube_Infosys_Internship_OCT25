import React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import theme from './styles/theme';
import Header from './components/Layout/Header';
import Sidebar from './components/Layout/Sidebar';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import VideosPage from './pages/VideosPage';
import SummaryPage from './pages/SummaryPage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

function App() {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0F0F0F' }}>
          <Header 
            onMenuClick={handleDrawerToggle}
            onSearchClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          />
          
          <Sidebar 
            mobileOpen={mobileOpen}
            onClose={() => setMobileOpen(false)}
          />
          
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - 240px)` },
              ml: { sm: '240px' },
              mt: '64px'
            }}
          >
            <Routes>
              <Route path="/" element={<SearchPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/videos" element={<VideosPage />} />
              <Route path="/summarize" element={<SummaryPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;