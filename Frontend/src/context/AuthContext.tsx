import React, { createContext, useContext, useState, useEffect } from 'react';

// 1. Roles
export type UserRole = 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';

// 2. User Type
export interface AuthUser {
  username: string;
  name: string;
  role: UserRole;
  avatarColor?: string;
}

// 3. Context Type
interface AuthContextType {
  user: AuthUser | null;
  login: (username: string, role: UserRole) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  // --- 🔥 CHANGE: Using sessionStorage instead of localStorage ---
  // Refresh කළාට මේක මැකෙන්නේ නෑ. (User stays logged in on refresh)
  // හැබැයි Tab එක වැහුවොත් මේක මැකෙනවා. (New session requires login)
  useEffect(() => {
    const storedUser = sessionStorage.getItem('bakeryUser'); // Changed to sessionStorage
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error("Failed to parse user data", error);
        sessionStorage.removeItem('bakeryUser');
      }
    }
  }, []);

  const login = (username: string, role: UserRole) => {
    let color = 'bg-gray-500';
    if (role === 'Manager') color = 'bg-purple-600';
    if (role === 'Cashier') color = 'bg-green-600';
    if (role === 'Baker') color = 'bg-orange-600';
    if (role === 'Storekeeper') color = 'bg-blue-600';

    const newUser: AuthUser = {
      username,
      name: username.charAt(0).toUpperCase() + username.slice(1),
      role,
      avatarColor: color
    };
    
    setUser(newUser);
    // Save to sessionStorage (Session only)
    sessionStorage.setItem('bakeryUser', JSON.stringify(newUser)); 
  };

  const logout = () => {
    setUser(null);
    sessionStorage.removeItem('bakeryUser'); // Clear from session
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};