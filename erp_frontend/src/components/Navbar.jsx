import React, { useContext } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext.jsx';

const navItems = [
  { label: 'Dashboard', path: '/' },
  { label: 'Students', path: '/students' },
  { label: 'Teachers', path: '/teachers' },
  { label: 'Timetable', path: '/timetable' },
  { label: 'Fees', path: '/fees' },
  { label: 'Exams', path: '/exams' },
  { label: 'Notices', path: '/notices' },
  { label: 'Events', path: '/events' },
];

export default function Navbar() {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            College ERP
          </Typography>
          {navItems.map((item) => (
            <Button color="inherit" key={item.path} component={RouterLink} to={item.path} sx={{ ml: 1 }}>
              {item.label}
            </Button>
          ))}
          {token ? (
            <Button color="inherit" onClick={handleLogout} sx={{ ml: 1 }}>
              Logout
            </Button>
          ) : (
            <Button color="inherit" component={RouterLink} to="/login" sx={{ ml: 1 }}>
              Login
            </Button>
          )}
        </Toolbar>
      </AppBar>
    </Box>
  );
}
