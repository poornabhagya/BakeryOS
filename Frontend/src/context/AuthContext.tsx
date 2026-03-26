import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient, { setTokens, clearTokens } from '../services/api';
import { UiUser } from '../utils/apiTypes';

// 1. Roles
export type UserRole = 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';

// 2. User Type (UI format)
export type AuthUser = UiUser;

// 3. Context Type
interface AuthContextType {
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize user from localStorage on mount
  useEffect(() => {
    const initializeAuth = () => {
      const storedUser = localStorage.getItem('bakeryUser');
      const accessToken = localStorage.getItem('access_token');
      
      if (storedUser && accessToken) {
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
        } catch (err) {
          console.error('Failed to parse stored user', err);
          localStorage.removeItem('bakeryUser');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
    };

    initializeAuth();
  }, []);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Call backend API (tokens are automatically stored in api.ts)
      const response = await apiClient.auth.login(username, password);
      
      // Extract data from response
      const { user } = response;

      // Store user in state and localStorage
      setUser(user);
      localStorage.setItem('bakeryUser', JSON.stringify(user));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Call backend logout
      await apiClient.auth.logout();
    } catch (err) {
      console.error('Logout error:', err);
      // Proceed with local cleanup even if API call fails
    } finally {
      // Clear local state and storage
      setUser(null);
      localStorage.removeItem('bakeryUser');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Clear API tokens
      clearTokens();
      
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading,
        error
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};