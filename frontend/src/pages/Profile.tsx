import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface Artwork {
  id: number;
  title: string;
  price: number;
  image_url: string;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  artworks: Artwork[];
  acquired_artworks: Artwork[];
}

const Profile: React.FC = () => {
  const { token, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated || !token) return;

    setLoading(true);
    fetch('http://127.0.0.1:8000/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      credentials: 'include'
    })
      .then(async res => {
        if (!res.ok) throw new Error('Failed to fetch profile');
        return res.json();
      })
      .then(data => {
        setProfile(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Error loading profile.');
        setLoading(false);
      });
  }, [isAuthenticated, token]);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading Profile...</div>;
  }

  if (error || !profile) {
    return <div style={{ textAlign: 'center', marginTop: '4rem', color: '#ef4444' }}>{error || 'Could not load profile.'}</div>;
  }

  const renderArtworkGrid = (artworks: Artwork[], emptyMessage: string) => {
    if (artworks.length === 0) {
      return <p style={{ color: 'var(--text-secondary)' }}>{emptyMessage}</p>;
    }
    return (
      <div className="artwork-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '2rem'
      }}>
        {artworks.map(art => (
          <Link to={`/artworks/${art.id}`} key={art.id} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="artwork-card animate-fade-in" style={{ borderRadius: '12px', overflow: 'hidden', background: 'rgba(255, 255, 255, 0.03)' }}>
              <div className="artwork-image-container" style={{ aspectRatio: '1/1', background: '#000' }}>
                <img 
                  src={art.image_url.startsWith('http') ? art.image_url : `http://127.0.0.1:8000${art.image_url}`} 
                  alt={art.title} 
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                />
              </div>
              <div style={{ padding: '1rem' }}>
                <div style={{ fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{art.title}</div>
                <div style={{ color: 'var(--accent-primary)', marginTop: '0.5rem' }}>${art.price.toLocaleString()}</div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    );
  };

  return (
    <div className="profile-container animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
      <div className="glass" style={{ padding: '2rem', borderRadius: '16px', marginBottom: '3rem', display: 'flex', alignItems: 'center', gap: '2rem' }}>
        <div style={{ 
          width: '100px', height: '100px', borderRadius: '50%', 
          background: 'var(--accent-primary)', display: 'flex', 
          justifyContent: 'center', alignItems: 'center',
          fontSize: '3rem', fontWeight: 'bold', color: '#fff' 
        }}>
          {profile.username.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 style={{ marginBottom: '0.5rem', fontSize: '2rem' }}>{profile.username}</h1>
          <p style={{ color: 'var(--text-secondary)' }}>{profile.email}</p>
        </div>
      </div>

      <div style={{ marginBottom: '4rem' }}>
        <h2 className="section-title" style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>My Collection</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Artworks you have acquired.</p>
        {renderArtworkGrid(profile.acquired_artworks, "You haven't acquired any artworks yet.")}
      </div>

      <div>
        <h2 className="section-title" style={{ fontSize: '1.75rem', marginBottom: '1.5rem' }}>My Portfolio</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Artworks you have posted for sale.</p>
        {renderArtworkGrid(profile.artworks, "You haven't posted any artworks yet.")}
      </div>
    </div>
  );
};

export default Profile;
