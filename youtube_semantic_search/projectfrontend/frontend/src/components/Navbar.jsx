import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Radio } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a1128]/80 backdrop-blur-md border-b border-cyan-500/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <Radio className="w-6 h-6 text-cyan-400 group-hover:text-cyan-300 transition-colors" />
            <span className="text-2xl font-bold text-cyan-400 group-hover:text-cyan-300 transition-colors">
              QueryTube AI
            </span>
          </Link>
          
          <div className="flex items-center gap-8">
            <Link
              to="/"
              className={`text-base font-medium transition-all duration-300 relative pb-1 ${
                isActive('/')
                  ? 'text-cyan-400'
                  : 'text-gray-300 hover:text-cyan-400'
              }`}
            >
              Home
              {isActive('/') && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
              )}
            </Link>
            
            <Link
              to="/upload"
              className={`text-base font-medium transition-all duration-300 relative pb-1 ${
                isActive('/upload')
                  ? 'text-cyan-400'
                  : 'text-gray-300 hover:text-cyan-400'
              }`}
            >
              Upload
              {isActive('/upload') && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
              )}
            </Link>
            
            <Link
              to="/search"
              className={`text-base font-medium transition-all duration-300 relative pb-1 ${
                isActive('/search')
                  ? 'text-cyan-400'
                  : 'text-gray-300 hover:text-cyan-400'
              }`}
            >
              Search
              {isActive('/search') && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
              )}
            </Link>
            
            <Link
              to="/summary"
              className={`text-base font-medium transition-all duration-300 relative pb-1 ${
                isActive('/summary')
                  ? 'text-cyan-400'
                  : 'text-gray-300 hover:text-cyan-400'
              }`}
            >
              Summary
              {isActive('/summary') && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.6)]" />
              )}
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
