import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  CircularProgress,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Tooltip
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Folder as FolderIcon } from '@mui/icons-material';
import Dropzone from '../components/Dropzone';
import api from '../api';

const formatDatabaseResponse = (dbs) => {
  if (!dbs) return [];
  if (Array.isArray(dbs)) {
    return dbs.map(db => ({
      name: typeof db === 'string' ? db : db.name || db,
      record_count: db.record_count || 0
    }));
  }
  return [];
};

function DatabaseManager() {
  const [databases, setDatabases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dbName, setDbName] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const fetchDatabases = async () => {
    try {
      setLoading(true);
      const response = await api.get('/health');
      const dbs = response.data.databases || response.data;
      setDatabases(formatDatabaseResponse(dbs));
      setError('');
    } catch (err) {
      console.error('Error fetching databases:', err);
      setError('Failed to fetch databases. Please check if the server is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, []);

  const handleFileSelected = (file) => {
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (!dbName.trim() || !selectedFile) {
      setSnackbar({
        open: true,
        message: 'Please provide a database name and select a file',
        severity: 'error',
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await api.post(`/create_db?collection_name=${encodeURIComponent(dbName)}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setSnackbar({
        open: true,
        message: 'Database created successfully!',
        severity: 'success',
      });
      
      setOpenDialog(false);
      setDbName('');
      setSelectedFile(null);
      fetchDatabases();
    } catch (err) {
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || 'Failed to create database',
        severity: 'error',
      });
    }
  };

  const handleDelete = async (dbName) => {
    if (!window.confirm(`Are you sure you want to delete the database "${dbName}"?`)) {
      return;
    }

    try {
      await api.delete(`/delete_db?collection_name=${encodeURIComponent(dbName)}`);
      fetchDatabases();
      setSnackbar({
        open: true,
        message: `Database "${dbName}" deleted successfully`,
        severity: 'success',
      });
    } catch (err) {
      console.error('Delete error:', err);
      setSnackbar({
        open: true,
        message: `Failed to delete database: ${err.response?.data?.detail || err.message}`,
        severity: 'error',
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="lg" className="fade-in">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4, mt: 2 }}>
        <Box>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 800, color: '#fff' }}>
            Databases
            </Typography>
            <Typography variant="body1" color="text.secondary">
            Manage your vector collections
            </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          sx={{ height: 48, px: 3 }}
        >
          New Database
        </Button>
      </Box>

      {error && <Alert severity="error" variant="filled" sx={{ mb: 3, borderRadius: 2 }}>{error}</Alert>}

      <Paper 
        sx={{ 
            width: '100%', 
            overflow: 'hidden', 
            borderRadius: '16px',
            backgroundColor: 'rgba(21, 26, 35, 0.6)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.05)'
        }}
      >
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ backgroundColor: '#1a1d2e', color: '#00f2ff', fontWeight: 600 }}>Name</TableCell>
                <TableCell sx={{ backgroundColor: '#1a1d2e', color: '#b0b8c4', fontWeight: 600 }}>Records</TableCell>
                <TableCell align="right" sx={{ backgroundColor: '#1a1d2e', color: '#b0b8c4', fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 8 }}>
                    <CircularProgress size={40} thickness={4} />
                    <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>Loading databases...</Typography>
                  </TableCell>
                </TableRow>
              ) : databases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 8 }}>
                    <FolderIcon sx={{ fontSize: 48, color: 'text.secondary', opacity: 0.5, mb: 1 }} />
                    <Typography variant="body1" color="text.secondary">No databases found</Typography>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => setOpenDialog(true)}
                      sx={{ mt: 2 }}
                    >
                      Create your first database
                    </Button>
                  </TableCell>
                </TableRow>
              ) : (
                databases.map((db) => {
                  const dbName = typeof db === 'string' ? db : db.name;
                  const recordCount = db.record_count || 0;
                  
                  return (
                    <TableRow 
                        key={dbName} 
                        hover
                        sx={{ 
                            '&:hover': { backgroundColor: 'rgba(255,255,255,0.03) !important' },
                            transition: 'background-color 0.2s'
                        }}
                    >
                      <TableCell sx={{ color: '#fff', fontSize: '1.05rem' }}>
                        <Box display="flex" alignItems="center" gap={2}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00f2ff', boxShadow: '0 0 8px #00f2ff' }} />
                            {dbName}
                        </Box>
                      </TableCell>
                      <TableCell sx={{ color: 'text.secondary' }}>{recordCount.toLocaleString()} records</TableCell>
                      <TableCell align="right">
                        <Tooltip title="Delete Database">
                            <IconButton
                            onClick={() => handleDelete(dbName)}
                            sx={{ color: '#ef5350', '&:hover': { bgcolor: 'rgba(239, 83, 80, 0.1)' } }}
                            >
                            <DeleteIcon />
                            </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog 
        open={openDialog} 
        onClose={() => setOpenDialog(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
            sx: {
                borderRadius: '24px',
                background: '#151a23',
                border: '1px solid rgba(255,255,255,0.1)'
            }
        }}
      >
        <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.05)', pb: 2 }}>Create New Database</DialogTitle>
        <DialogContent sx={{ pt: 4 }}>
          <Box sx={{ mt: 2, mb: 3 }}>
            <Typography gutterBottom sx={{ color: '#00f2ff', fontSize: '0.9rem', fontWeight: 600 }}>DATABASE NAME</Typography>
            <TextField
              fullWidth
              variant="outlined"
              value={dbName}
              onChange={(e) => setDbName(e.target.value)}
              placeholder="e.g., tutorial_videos"
              sx={{ mt: 1 }}
            />
          </Box>
          <Box sx={{ mt: 4, mb: 2 }}>
            <Typography gutterBottom sx={{ color: '#00f2ff', fontSize: '0.9rem', fontWeight: 600, mb: 2 }}>UPLOAD DATASET (CSV)</Typography>
            <Dropzone onFileSelected={handleFileSelected} />
            {selectedFile && (
                <Typography variant="body2" sx={{ mt: 2, color: '#4caf50', display: 'flex', alignItems: 'center', gap: 1 }}>
                    ✓ Selected: {selectedFile.name}
                </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <Button onClick={() => setOpenDialog(false)} sx={{ color: 'text.secondary' }}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!dbName.trim() || !selectedFile}
            sx={{ px: 4 }}
          >
            Create Database
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity} 
          variant="filled"
          sx={{ width: '100%', borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default DatabaseManager;