// Centralized API calls for ERP backend
import axios from 'axios';

const API_BASE = 'http://localhost:8888/api'; // Update if backend URL changes

export const api = axios.create({
  baseURL: API_BASE,
});

// Example: Auth endpoints
export const login = (username, password) =>
  api.post('/auth/login/', { username, password });

export const refresh = (refresh) =>
  api.post('/auth/refresh/', { refresh });

// Add more API methods as needed (students, teachers, timetable, etc.)
