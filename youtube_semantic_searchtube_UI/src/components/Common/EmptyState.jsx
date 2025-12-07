import React from 'react';
import {
  Box,
  Typography,
  Button
} from '@mui/material';
import {
  Search as SearchIcon,
  YouTube,
  Summarize
} from '@mui/icons-material';

const EmptyState = ({ 
  title, 
  description, 
  icon = 'search',
  actionLabel,
  onAction 
}) => {
  const getIcon = () => {
    switch (icon) {
      case 'youtube':
        return <YouTube sx={{ fontSize: 80, color: '#FF0000' }} />;
      case 'summarize':
        return <Summarize sx={{ fontSize: 80, color: '#FF0000' }} />;
      default:
        return <SearchIcon sx={{ fontSize: 80, color: '#666666' }} />;
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 10,
        px: 2,
        textAlign: 'center'
      }}
    >
      {getIcon()}
      
      <Typography 
        variant="h5" 
        sx={{ 
          mt: 3, 
          mb: 1,
          fontWeight: 600 
        }}
      >
        {title}
      </Typography>
      
      <Typography 
        variant="body1" 
        color="text.secondary"
        sx={{ 
          maxWidth: 500,
          mb: 3
        }}
      >
        {description}
      </Typography>
      
      {actionLabel && onAction && (
        <Button
          variant="contained"
          startIcon={icon === 'search' ? <SearchIcon /> : <Summarize />}
          onClick={onAction}
          sx={{
            backgroundColor: '#FF0000',
            '&:hover': {
              backgroundColor: '#CC0000'
            }
          }}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  );
};

export default EmptyState;