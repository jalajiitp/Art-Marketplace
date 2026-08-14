import React, { createContext, useState, useEffect, useContext } from 'react';

interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Attempt silent refresh on initial load
    const silentRefresh = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/auth/refresh', {
          method: 'GET',
          credentials: 'include',
        });
        if (res.ok) {
          const data = await res.json();
          setToken(data.access_token);
        }
      } catch (err) {
        console.error("Silent refresh failed:", err);
      } finally {
        setLoading(false);
      }
    };
    silentRefresh();
  }, []);

  const login = (newToken: string) => {
    setToken(newToken);
  };

  const logout = async () => {
    try {
      await fetch('http://127.0.0.1:8000/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      console.error("Logout failed:", err);
    }
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, isAuthenticated: !!token, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
