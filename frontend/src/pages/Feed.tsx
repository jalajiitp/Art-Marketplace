import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface Artwork {
  id: number;
  title: string;
  description: string;
  price: number;
  image_url: string;
  artist_id: number;
}

const Feed: React.FC = () => {
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const { token } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const search = params.get('search');
    let url = 'http://127.0.0.1:8000/artworks/feed';
    if (search) {
      url += `?search=${encodeURIComponent(search)}`;
    }

    setLoading(true);
    
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    fetch(url, {
      headers,
      credentials: 'include'
    })
      .then(res => res.json())
      .then(data => {
        setArtworks(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching artworks:", err);
        setLoading(false);
      });
  }, [location.search, token]);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading Gallery...</div>;
  }

  return (
    <div>
      <div className="section-title">Discovery Feed</div>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Curated artwork tailored to your aesthetic tastes.
      </p>

      {artworks.length === 0 ? (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '4rem' }}>
          No artworks found. Be the first to upload!
        </div>
      ) : (
        <div className="masonry-grid">
          {artworks.map(art => (
            <Link key={art.id} to={`/artworks/${art.id}`} style={{ textDecoration: 'none' }}>
              <div className="artwork-card glass">
                <div className="artwork-image-container">
                  <img 
                    src={art.image_url.startsWith('http') ? art.image_url : `http://127.0.0.1:8000${art.image_url}`} 
                    alt={art.title} 
                    className="artwork-img"
                    loading="lazy"
                  />
                  <div className="artwork-overlay">
                    <h3 className="artwork-title">{art.title}</h3>
                    <div className="artwork-artist">By Artist #{art.artist_id}</div>
                    <div style={{ marginTop: '0.5rem', fontWeight: 600, color: 'var(--accent-secondary)' }}>
                      ${art.price}
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Feed;
