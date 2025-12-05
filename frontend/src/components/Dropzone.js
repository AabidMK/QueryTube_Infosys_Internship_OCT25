import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Paper, Typography, Box } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

function Dropzone({ onFileSelected }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onFileSelected(acceptedFiles[0]);
    }
  }, [onFileSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  return (
    <Paper
      {...getRootProps()}
      sx={{
        p: 6,
        border: '2px dashed',
        borderColor: isDragActive ? '#00f2ff' : 'rgba(255, 255, 255, 0.2)',
        borderRadius: '20px',
        textAlign: 'center',
        cursor: 'pointer',
        backgroundColor: isDragActive ? 'rgba(0, 242, 255, 0.05)' : 'rgba(0,0,0,0.2)',
        transition: 'all 0.3s ease',
        '&:hover': {
          borderColor: '#00f2ff',
          backgroundColor: 'rgba(0, 242, 255, 0.05)',
          transform: 'scale(1.01)'
        },
      }}
    >
      <input {...getInputProps()} />
      <Box sx={{ color: isDragActive ? '#00f2ff' : 'text.secondary' }}>
        <CloudUploadIcon sx={{ 
          fontSize: 64, 
          mb: 2, 
          color: isDragActive ? '#00f2ff' : 'rgba(255,255,255,0.5)',
          filter: isDragActive ? 'drop-shadow(0 0 10px rgba(0,242,255,0.5))' : 'none',
          transition: 'all 0.3s'
        }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? 'Drop the CSV file here...'
            : 'Drag & Drop CSV File'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ opacity: 0.7 }}>
          or click to browse your system
        </Typography>
      </Box>
    </Paper>
  );
}

export default Dropzone;