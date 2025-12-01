import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import SearchPage from './components/SearchPage';
import UploadPage from './components/UploadPage';
import HealthPage from './components/HealthPage';
import './styles/App.css';

function App() {
  return (
    <div className="App">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/health" element={<HealthPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;