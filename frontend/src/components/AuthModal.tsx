import React, { useState } from 'react';

interface AuthModalProps {
  onClose: () => void;
  onSuccess: (token: string) => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ onClose, onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const res = await fetch('http://127.0.0.1:8000/auth/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          credentials: 'include',
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        onSuccess(data.access_token);
      } else {
        // Register
        const res = await fetch('http://127.0.0.1:8000/users/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ username, email, password }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Registration failed');
        
        // Auto-login after register
        const loginData = new URLSearchParams();
        loginData.append('username', username);
        loginData.append('password', password);
        const loginRes = await fetch('http://127.0.0.1:8000/auth/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          credentials: 'include',
          body: loginData,
        });
        const loginResData = await loginRes.json();
        if (!loginRes.ok) throw new Error(loginResData.detail || 'Login failed');
        onSuccess(loginResData.access_token);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(10px)',
      zIndex: 200, display: 'flex', justifyContent: 'center', alignItems: 'center',
      padding: '2rem'
    }} onClick={onClose}>
      <div className="glass animate-fade-in" style={{ width: '100%', maxWidth: '400px', padding: '2rem', borderRadius: '16px' }} onClick={e => e.stopPropagation()}>
        <div className="section-title">{isLogin ? 'Welcome Back' : 'Join Discovery Engine'}</div>
        
        {error && <div style={{ color: '#ef4444', marginBottom: '1rem', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input type="text" className="form-input" value={username} onChange={e => setUsername(e.target.value)} required />
          </div>
          
          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Email</label>
              <input type="email" className="form-input" value={email} onChange={e => setEmail(e.target.value)} required />
            </div>
          )}
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" className="form-input" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginBottom: '1rem' }} disabled={loading}>
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Register')}
          </button>
          
          <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <span style={{ color: 'var(--accent-primary)', cursor: 'pointer', fontWeight: 'bold' }} onClick={() => setIsLogin(!isLogin)}>
              {isLogin ? 'Register' : 'Login'}
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;
