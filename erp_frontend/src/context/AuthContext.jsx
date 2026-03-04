import React, { createContext, useState, useEffect } from 'react';
import { login as apiLogin, refresh as apiRefresh } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access') || null);

  useEffect(() => {
    if (token) {
      setUser({}); // Optionally fetch user profile here
    }
  }, [token]);

  const login = async (username, password) => {
    const res = await apiLogin(username, password);
    setToken(res.data.access);
    localStorage.setItem('access', res.data.access);
    localStorage.setItem('refresh', res.data.refresh);
    setUser({}); // Optionally fetch user profile here
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
