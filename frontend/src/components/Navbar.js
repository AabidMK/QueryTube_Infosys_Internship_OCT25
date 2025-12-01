import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return 'nav-link active';
    if (path !== '/' && location.pathname.startsWith(path)) return 'nav-link active';
    return 'nav-link';
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="logo">
          <span className="logo-icon">🎬</span>
          QueryTube:AI
        </Link>
        
        <ul className="nav-links">
          <li>
            <Link to="/" className={isActive('/')}>
              🏠 Home
            </Link>
          </li>
          <li>
            <Link to="/search" className={isActive('/search')}>
              🔍 Semantic Search
            </Link>
          </li>
          <li>
            <Link to="/upload" className={isActive('/upload')}>
              📤 Upload CSV
            </Link>
          </li>
          <li>
            <Link to="/health" className={isActive('/health')}>
              💓 Health Check
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;