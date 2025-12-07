import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Box,
  Badge
} from '@mui/material';
import { 
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  YouTube
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Header = ({ onMenuClick, onSearchClick }) => {
  const navigate = useNavigate();

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        backgroundColor: '#0F0F0F',
        borderBottom: '1px solid #333333'
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={onMenuClick}
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>

        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer',
            mr: 3 
          }}
          onClick={() => navigate('/')}
        >
          <YouTube sx={{ color: '#FF0000', fontSize: 32, mr: 1 }} />
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(45deg, #FF0000, #FF6B6B)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}
          >
            YouTube Semantic Search
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <IconButton 
          color="inherit" 
          onClick={onSearchClick}
          sx={{ mr: 2 }}
        >
          <SearchIcon />
        </IconButton>

        <IconButton color="inherit" sx={{ mr: 2 }}>
          <Badge badgeContent={3} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>

        <IconButton color="inherit">
          <AccountCircle />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
};

export default Header;