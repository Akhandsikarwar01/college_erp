# ERP Frontend (React + Vite)

This is the frontend for the College ERP system, built with React, Vite, and Material UI.

## Features
- Modern React app with Vite for fast development
- Material UI for a clean, professional look
- React Router for navigation
- JWT authentication context (ready to connect to backend)
- Pages: Dashboard, Students, Teachers, Timetable, Fees, Exams, Notices, Events, Login
- Centralized API service for backend integration

## Getting Started

1. Install dependencies:
   ```sh
   npm install
   ```
2. Start the development server:
   ```sh
   npm run dev
   ```
3. The app will be available at [http://localhost:5173](http://localhost:5173)

## Project Structure
- `src/pages/` — Main pages (Dashboard, Students, etc.)
- `src/components/` — Reusable UI components
- `src/services/` — API calls to Django backend
- `src/context/` — Authentication context
- `src/assets/` — Images and static assets

## Backend API
- Expects Django backend running at `http://localhost:8888/api/`
- Update `API_BASE` in `src/services/api.js` if backend URL changes

---

Replace placeholder content and expand pages/components as needed for your ERP features.
