import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Upload: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !price || !file) {
      setError('Please fill in all required fields.');
      return;
    }

    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('price', price);
    formData.append('file', file);

    try {
      const res = await fetch('http://127.0.0.1:8000/artworks/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed.');
      }

      navigate('/');
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
      <div className="section-title">Upload Artwork</div>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Add your piece to the discovery engine. Our system will generate text embeddings to find similar artworks.
      </p>

      <form onSubmit={handleSubmit} className="glass" style={{ padding: '2rem', borderRadius: '16px' }}>
        {error && <div style={{ color: '#ef4444', marginBottom: '1rem', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
        
        <div className="form-group">
          <label className="form-label">Artwork Title *</label>
          <input 
            type="text" 
            className="form-input" 
            value={title} 
            onChange={(e) => setTitle(e.target.value)} 
            placeholder="E.g., Neon Genesis" 
          />
        </div>

        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea 
            className="form-textarea" 
            rows={4} 
            value={description} 
            onChange={(e) => setDescription(e.target.value)} 
            placeholder="Tell the story behind this piece..." 
          />
        </div>

        <div className="form-group">
          <label className="form-label">Price (USD) *</label>
          <input 
            type="number" 
            step="0.01" 
            className="form-input" 
            value={price} 
            onChange={(e) => setPrice(e.target.value)} 
            placeholder="0.00" 
          />
        </div>

        <div className="form-group">
          <label className="form-label">Image File *</label>
          <input 
            type="file" 
            accept="image/*" 
            className="form-input" 
            onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} 
            style={{ padding: '0.5rem' }}
          />
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
          {loading ? 'Uploading & Generating Embeddings...' : 'Upload & Analyze'}
        </button>
      </form>
    </div>
  );
};

export default Upload;
