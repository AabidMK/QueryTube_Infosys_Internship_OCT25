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
        p: 4,
        border: '2px dashed #ccc',
        textAlign: 'center',
        cursor: 'pointer',
        backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
        '&:hover': {
          backgroundColor: 'action.hover',
        },
      }}
    >
      <input {...getInputProps()} />
      <Box sx={{ color: 'text.secondary' }}>
        <CloudUploadIcon sx={{ fontSize: 48, mb: 1 }} />
        <Typography>
          {isDragActive
            ? 'Drop the CSV file here...'
            : 'Drag and drop a CSV file here, or click to select'}
        </Typography>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Only .csv files are accepted
        </Typography>
      </Box>
    </Paper>
  );
}

export default Dropzone;
