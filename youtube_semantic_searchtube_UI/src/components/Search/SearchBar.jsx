import React, { useState } from 'react';
import {
  Paper,
  InputBase,
  IconButton,
  Box,
  CircularProgress,
  Chip,
  Typography
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SearchBar = ({ 
  onSearch, 
  isLoading, 
  recentSearches = [],
  onRecentSearchClick 
}) => {
  const [query, setQuery] = useState('');
  const [showRecent, setShowRecent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    setShowRecent(false);
  };

  return (
    <Box sx={{ position: 'relative', width: '100%', maxWidth: 800, mx: 'auto' }}>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Paper
          component="form"
          onSubmit={handleSubmit}
          sx={{
            p: '2px 4px',
            display: 'flex',
            alignItems: 'center',
            backgroundColor: '#212121',
            border: '2px solid #333333',
            '&:hover': {
              borderColor: '#FF0000'
            }
          }}
        >
          <IconButton sx={{ p: '10px', color: '#FF0000' }}>
            <SearchIcon />
          </IconButton>
          
          <InputBase
            sx={{ ml: 1, flex: 1, color: 'white' }}
            placeholder="Search my topic"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setShowRecent(true)}
            autoComplete="off"
          />
          
          {query && (
            <IconButton onClick={handleClear}>
              <ClearIcon />
            </IconButton>
          )}
          
          <IconButton 
            type="submit" 
            sx={{ p: '10px', color: '#FF0000' }}
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              <Typography sx={{ fontWeight: 600 }}>Search</Typography>
            )}
          </IconButton>
        </Paper>
      </motion.div>

      {/* Recent Searches */}
      {showRecent && recentSearches.length > 0 && (
        <Paper
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            p: 2,
            backgroundColor: '#212121',
            border: '1px solid #333333',
            zIndex: 1000
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <FilterIcon sx={{ mr: 1, fontSize: 18 }} />
            <Typography variant="body2" color="text.secondary">
              Recent Searches
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {recentSearches.map((search, index) => (
              <Chip
                key={index}
                label={search}
                size="small"
                onClick={() => {
                  setQuery(search);
                  onRecentSearchClick(search);
                  setShowRecent(false);
                }}
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 0, 0, 0.2)'
                  }
                }}
              />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default SearchBar;