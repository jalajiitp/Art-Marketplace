import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface CheckoutModalProps {
  artworkId: number;
  artworkTitle: string;
  price: number;
  onClose: () => void;
}

const CheckoutModal: React.FC<CheckoutModalProps> = ({ artworkId, artworkTitle, price, onClose }) => {
  const { token } = useAuth();
  
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvc, setCvc] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !address || !cardNumber || !expiry || !cvc) {
      setError('Please fill in all fields.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/artworks/${artworkId}/purchase`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });
      
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Purchase failed.');
      }
      
      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 3000);
      
    } catch (err: any) {
      setError(err.message || 'An error occurred during checkout.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)',
        zIndex: 200, display: 'flex', justifyContent: 'center', alignItems: 'center',
        padding: '2rem'
      }} onClick={onClose}>
        <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '400px', padding: '3rem 2rem', borderRadius: '16px', textAlign: 'center' }} onClick={e => e.stopPropagation()}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎉</div>
          <h2 style={{ marginBottom: '1rem' }}>Purchase Successful!</h2>
          <p style={{ color: 'var(--text-secondary)' }}>You have successfully acquired <strong>{artworkTitle}</strong>.</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)',
      zIndex: 200, display: 'flex', justifyContent: 'center', alignItems: 'center',
      padding: '2rem'
    }} onClick={onClose}>
      <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '500px', padding: '2rem', borderRadius: '16px', maxHeight: '90vh', overflowY: 'auto' }} onClick={e => e.stopPropagation()}>
        <div className="section-title">Secure Checkout</div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
          <div>
            <div style={{ fontWeight: 600 }}>{artworkTitle}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Artwork Acquisition</div>
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--accent-primary)' }}>
            ${price.toLocaleString()}
          </div>
        </div>
        
        {error && <div style={{ color: '#ef4444', marginBottom: '1rem', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Shipping Details</h3>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input type="text" className="form-input" value={name} onChange={e => setName(e.target.value)} placeholder="Jane Doe" required />
          </div>
          <div className="form-group" style={{ marginBottom: '2rem' }}>
            <label className="form-label">Address</label>
            <input type="text" className="form-input" value={address} onChange={e => setAddress(e.target.value)} placeholder="123 Art Lane, NY" required />
          </div>
          
          <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Payment Information</h3>
          <div className="form-group">
            <label className="form-label">Card Number</label>
            <input type="text" className="form-input" value={cardNumber} onChange={e => setCardNumber(e.target.value)} placeholder="0000 0000 0000 0000" maxLength={19} required />
          </div>
          
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Expiry</label>
              <input type="text" className="form-input" value={expiry} onChange={e => setExpiry(e.target.value)} placeholder="MM/YY" maxLength={5} required />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">CVC</label>
              <input type="text" className="form-input" value={cvc} onChange={e => setCvc(e.target.value)} placeholder="123" maxLength={4} required />
            </div>
          </div>
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }} disabled={loading}>
            {loading ? 'Processing...' : `Pay $${price.toLocaleString()}`}
          </button>
          
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <span style={{ color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.9rem' }} onClick={onClose}>
              Cancel
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CheckoutModal;
