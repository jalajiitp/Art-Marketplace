import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import Navbar from './components/Navbar';
import Feed from './pages/Feed';
import ArtworkDetail from './pages/ArtworkDetail';
import Upload from './pages/Upload';
import Profile from './pages/Profile';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
};

const AppContent = () => {
  const { isAuthenticated, logout, login } = useAuth();
  const [showAuth, setShowAuth] = useState(false);

  return (
    <div className="app-container">
      <Navbar 
        isLoggedIn={isAuthenticated}
        onLogout={logout}
        onLoginClick={() => setShowAuth(true)}
      />
      
      <main className="main-content animate-fade-in">
        <Routes>
          <Route path="/" element={<Feed />} />
          <Route path="/artworks/:id" element={<ArtworkDetail />} />
          <Route 
            path="/upload" 
            element={
              <ProtectedRoute>
                <Upload />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </main>

      {showAuth && (
        <AuthModal 
          onClose={() => setShowAuth(false)} 
          onSuccess={(token) => {
            login(token);
            setShowAuth(false);
          }} 
        />
      )}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
