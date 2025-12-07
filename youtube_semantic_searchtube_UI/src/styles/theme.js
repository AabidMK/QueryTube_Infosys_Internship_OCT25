import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF0000', // YouTube red
      light: '#FF3333',
      dark: '#CC0000',
    },
    secondary: {
      main: '#282828',
      light: '#404040',
      dark: '#1C1C1C',
    },
    background: {
      default: '#0F0F0F',
      paper: '#212121',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#AAAAAA',
    },
    success: {
      main: '#00D100',
    },
    warning: {
      main: '#FFD600',
    },
    error: {
      main: '#FF3333',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Segoe UI", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
    body1: {
      fontSize: '0.95rem',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#212121',
          backgroundImage: 'none',
          border: '1px solid #333333',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(255, 0, 0, 0.3)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
  },
});

export default theme;