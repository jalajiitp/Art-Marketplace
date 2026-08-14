import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AuthModal from '../components/AuthModal';
import CheckoutModal from '../components/CheckoutModal';

interface Artwork {
  id: number;
  title: string;
  description: string;
  price: number;
  image_url: string;
  artist_id: number;
  likes_count: number;
}

const ArtworkDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [artwork, setArtwork] = useState<Artwork | null>(null);
  const [recommendations, setRecommendations] = useState<Artwork[]>([]);
  const [loading, setLoading] = useState(true);
  
  const { isAuthenticated, login, token } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [isLiking, setIsLiking] = useState(false);

  const handleAcquire = () => {
    if (!isAuthenticated) {
      setShowAuth(true);
    } else {
      setShowCheckout(true);
    }
  };

  const handleLike = () => {
    if (!isAuthenticated) {
      setShowAuth(true);
      return;
    }
    
    setIsLiking(true);
    fetch(`http://127.0.0.1:8000/artworks/${id}/like`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      credentials: 'include'
    })
    .then(res => res.json())
    .then(data => {
      if (artwork && data.likes_count !== undefined) {
        setArtwork({ ...artwork, likes_count: data.likes_count });
      } else if (artwork && data.message === "Liked successfully") {
        setArtwork({ ...artwork, likes_count: artwork.likes_count + 1 });
      } else if (artwork && data.message === "Unliked successfully") {
        setArtwork({ ...artwork, likes_count: Math.max(0, artwork.likes_count - 1) });
      }
      setIsLiking(false);
    })
    .catch(err => {
      console.error(err);
      setIsLiking(false);
    });
  };

  useEffect(() => {
    // We fetch all artworks to find the one we want.
    // In a real app we'd have a GET /artworks/:id endpoint.
    // Actually, let's assume we can fetch all and filter for now, or just fetch all and find it
    setLoading(true);
    fetch(`http://127.0.0.1:8000/artworks/`)
      .then(res => res.json())
      .then((data: Artwork[]) => {
        const found = data.find(a => a.id.toString() === id);
        if (found) {
          setArtwork(found);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching artwork details:", err);
        setLoading(false);
      });
  }, [id]);

  useEffect(() => {
    if (id) {
      setRecommendations([]);
      fetch(`http://127.0.0.1:8000/artworks/${id}/recommendations/?limit=4`)
        .then(res => res.json())
        .then(data => setRecommendations(data))
        .catch(err => console.error("Error fetching recommendations:", err));
    }
  }, [id]);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading Artwork...</div>;
  }

  if (!artwork) {
    return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Artwork not found.</div>;
  }

  return (
    <div className="artwork-detail-container animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="glass" style={{ borderRadius: '16px', overflow: 'hidden' }}>
        <div style={{ background: '#000', textAlign: 'center', padding: '2rem' }}>
          <img 
            src={artwork.image_url.startsWith('http') ? artwork.image_url : `http://127.0.0.1:8000${artwork.image_url}`} 
            alt={artwork.title}
            style={{ maxHeight: '600px', maxWidth: '100%', objectFit: 'contain' }}
          />
        </div>
        <div style={{ padding: '2rem' }}>
          <h2>{artwork.title}</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Artist #{artwork.artist_id} • ${artwork.price}
          </p>
          <p>{artwork.description || 'No description provided.'}</p>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
            <button 
              className="btn btn-primary" 
              style={{ flex: 1, padding: '1rem' }}
              onClick={handleAcquire}
            >
              Acquire Artwork
            </button>
            <button 
              className="btn btn-outline"
              style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              onClick={handleLike}
              disabled={isLiking}
            >
              ❤️ {artwork.likes_count}
            </button>
          </div>

          {/* Recommendations Section */}
          {recommendations.length > 0 && (
            <div className="recommendations-section" style={{ marginTop: '3rem' }}>
              <div className="section-title" style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Visually Similar</div>
              <div style={{ display: 'flex', gap: '1rem', overflowX: 'auto', paddingBottom: '1rem' }}>
                {recommendations.map(rec => (
                  <Link 
                    key={rec.id} 
                    to={`/artworks/${rec.id}`}
                    style={{ textDecoration: 'none', color: 'inherit' }}
                  >
                    <div 
                      className="artwork-card" 
                      style={{ minWidth: '200px', flexShrink: 0, overflow: 'hidden', borderRadius: '8px' }}
                    >
                      <div className="artwork-image-container" style={{ aspectRatio: '1/1' }}>
                        <img 
                          src={rec.image_url.startsWith('http') ? rec.image_url : `http://127.0.0.1:8000${rec.image_url}`} 
                          alt={rec.title} 
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                        />
                      </div>
                      <div style={{ padding: '1rem', background: 'var(--bg-secondary)' }}>
                        <div style={{ fontWeight: 600 }}>{rec.title}</div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {showAuth && (
        <AuthModal 
          onClose={() => setShowAuth(false)} 
          onSuccess={(token) => {
            login(token);
            setShowAuth(false);
            setShowCheckout(true);
          }} 
        />
      )}
      
      {showCheckout && (
        <CheckoutModal 
          artworkId={artwork.id}
          artworkTitle={artwork.title}
          price={artwork.price}
          onClose={() => setShowCheckout(false)}
        />
      )}
    </div>
  );
};

export default ArtworkDetail;
