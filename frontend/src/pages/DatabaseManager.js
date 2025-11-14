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
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Refresh as RefreshIcon } from '@mui/icons-material';
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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Video Databases
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          New Database
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                    <Typography variant="body2" sx={{ mt: 1 }}>Loading databases...</Typography>
                  </TableCell>
                </TableRow>
              ) : databases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1">No databases found</Typography>
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
                    <TableRow key={dbName} hover>
                      <TableCell>{dbName}</TableCell>
                      <TableCell>{recordCount} records</TableCell>
                      <TableCell>
                        <Button
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDelete(dbName)}
                          size="small"
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Database</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, mb: 3 }}>
            <Typography gutterBottom>Database Name</Typography>
            <TextField
              fullWidth
              variant="outlined"
              value={dbName}
              onChange={(e) => setDbName(e.target.value)}
              placeholder="Enter a name for your database"
            />
          </Box>
          <Box sx={{ mt: 3, mb: 2 }}>
            <Typography gutterBottom>Upload CSV File</Typography>
            <Dropzone onFileSelected={handleFileSelected} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!dbName.trim() || !selectedFile}
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
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default DatabaseManager;