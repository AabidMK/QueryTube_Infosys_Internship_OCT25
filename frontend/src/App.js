// src/App.js
import React from 'react';
import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import Home from './pages/Home';
import Search from './pages/Search';
import Upload from './pages/Upload';
import Summary from './pages/Summary';

import { Toaster } from './components/ui/sonner';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        {/* Global Navbar (links to /, /search, /upload, /summary) */}
        <Navbar />

        {/* Page Routes */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/summary" element={<Summary />} />
        </Routes>

        {/* Global toast container */}
        <Toaster />
      </BrowserRouter>
    </div>
  );
}

export default App;
