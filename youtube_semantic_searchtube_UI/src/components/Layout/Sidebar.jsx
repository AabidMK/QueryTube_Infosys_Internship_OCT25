import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  ListItemButton  // ADD THIS
} from '@mui/material';
import {
  Home,
  Search,
  VideoLibrary,
  Summarize,
  Dashboard,
  Settings,
  Help,
  YouTube,
  History,
  ThumbUp
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const menuItems = [
  { text: 'Home', icon: <Home />, path: '/' },
  { text: 'Search', icon: <Search />, path: '/search' },
  { text: 'Videos', icon: <VideoLibrary />, path: '/videos' },
  { text: 'Summarize', icon: <Summarize />, path: '/summarize' },
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
];

const secondaryItems = [
  { text: 'History', icon: <History /> },
  { text: 'Liked Videos', icon: <ThumbUp /> },
  { text: 'Settings', icon: <Settings /> },
  { text: 'Help', icon: <Help /> },
];

const Sidebar = ({ mobileOpen, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const drawer = (
    <Box sx={{ overflowX: 'hidden' }}>
      {/* Logo */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
        <YouTube sx={{ color: '#FF0000', fontSize: 32, mr: 1 }} />
        <Typography variant="h6" sx={{ fontWeight: 700 }}>
          YT Search
        </Typography>
      </Box>

      <Divider sx={{ borderColor: '#333333' }} />

      {/* Main Menu */}
      <List>
        {menuItems.map((item) => (
          <ListItem 
            key={item.text}
            disablePadding
            onClick={() => {
              navigate(item.path);
              onClose();
            }}
          >
            <ListItemButton
              sx={{
                mb: 0.5,
                backgroundColor: location.pathname === item.path ? 'rgba(255, 0, 0, 0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255, 0, 0, 0.2)',
                }
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#FF0000' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                sx={{
                  '& .MuiTypography-root': {
                    fontWeight: location.pathname === item.path ? 600 : 400,
                    color: location.pathname === item.path ? '#FF0000' : 'inherit'
                  }
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider sx={{ borderColor: '#333333', my: 2 }} />

      {/* Secondary Menu */}
      <List>
        <ListItem>
          <Typography variant="caption" color="text.secondary">
            LIBRARY
          </Typography>
        </ListItem>
        {secondaryItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton sx={{ mb: 0.5 }}>
              <ListItemIcon sx={{ color: 'text.secondary' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider sx={{ borderColor: '#333333', my: 2 }} />

      {/* Stats */}
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block">
          Database Stats
        </Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          615+ videos indexed
        </Typography>
        <Typography variant="body2">
          AI Summarization: Active
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box
      component="nav"
      sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
    >
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: '#1C1C1C',
            borderRight: '1px solid #333333',
          },
        }}
      >
        {drawer}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: drawerWidth,
            backgroundColor: '#1C1C1C',
            borderRight: '1px solid #333333',
          },
        }}
        open
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Sidebar;