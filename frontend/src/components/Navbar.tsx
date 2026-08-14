import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface NavbarProps {
  isLoggedIn: boolean;
  onLogout: () => void;
  onLoginClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ isLoggedIn, onLogout, onLoginClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate(`/`);
    }
  };

  return (
    <nav className="navbar glass">
      <div className="navbar-container" style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
        <Link to="/" className="navbar-brand">
          ArtDiscovery
        </Link>
        
        <form onSubmit={handleSearch} style={{ flex: 1, maxWidth: '400px', margin: '0 2rem' }}>
          <input 
            type="text" 
            placeholder="Search artworks..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.6rem 1.2rem',
              borderRadius: '20px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'inherit',
              outline: 'none',
              transition: 'border-color 0.2s'
            }}
            onFocus={(e) => e.target.style.borderColor = 'var(--accent-primary)'}
            onBlur={(e) => e.target.style.borderColor = 'rgba(255, 255, 255, 0.2)'}
          />
        </form>

        <div className="nav-links">
          <Link to="/" className="btn btn-outline">Feed</Link>
          {isLoggedIn ? (
            <>
              <Link to="/profile" className="btn btn-outline">Profile</Link>
              <Link to="/upload" className="btn btn-primary">Upload Art</Link>
              <button onClick={onLogout} className="btn btn-outline">Logout</button>
            </>
          ) : (
            <button onClick={onLoginClick} className="btn btn-primary">Login / Register</button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
