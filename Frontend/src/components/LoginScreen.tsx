import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ChefHat, Lock, User, AlertCircle, Loader } from 'lucide-react';

export function LoginScreen() {
  const { login, isLoading } = useAuth();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); // Clear previous errors

    // Validate inputs
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      return;
    }

    try {
      // Call real backend API
      await login(username, password);
      
      // Successful login - component will re-render automatically
      // because user state changed in AuthContext
      // Clear form
      setUsername('');
      setPassword('');
    } catch (err) {
      // Error is handled by auth context, display it here
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setError(errorMessage);
    }
  };

  return (
    <div className="relative min-h-screen bg-orange-50 flex items-center justify-center p-4 overflow-hidden">
      
      {/* --- BACKGROUND DECORATION --- */}
      <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-orange-300 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-96 h-96 bg-amber-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      
      {/* Main Card */}
      <div className="relative z-10 bg-white/80 backdrop-blur-md w-full max-w-md p-8 rounded-[40px] shadow-2xl shadow-orange-200/50 border border-white/60">
        
        {/* Logo Section */}
        <div className="flex flex-col items-center mb-8">
          <div className="bg-orange-600 bg-gradient-to-r from-orange-500 to-orange-600 p-4 rounded-3xl shadow-lg shadow-orange-500/30 mb-4 transform rotate-3 transition-transform hover:rotate-6">
            <ChefHat className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">BakeryOS</h1>
          <p className="text-gray-500 text-sm mt-1 font-medium">Sign in to continue</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-6">
          
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-4 flex items-center gap-3 animate-in fade-in zoom-in-95 duration-200">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <p className="text-sm text-red-700 font-medium">{error}</p>
            </div>
          )}

          {/* Username Input */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2 ml-4">Username</label>
            <div className="relative group">
              <User className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-orange-500 transition-colors z-10" />
              <input 
                type="text" 
                required
                disabled={isLoading}
                style={{ paddingLeft: '3.5rem' }} 
                className="w-full border-2 border-gray-100 bg-white/60 rounded-full pr-6 py-3 focus:ring-4 focus:ring-orange-100 focus:border-orange-500 outline-none transition-all font-medium text-gray-700 placeholder-gray-400 backdrop-blur-sm disabled:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setError(''); // Clear error on input
                }}
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-bold text-gray-700 mb-2 ml-4">Password</label>
            <div className="relative group">
              <Lock className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 group-focus-within:text-orange-500 transition-colors z-10" />
              <input 
                type="password" 
                required
                disabled={isLoading}
                style={{ paddingLeft: '3.5rem' }} 
                className="w-full border-2 border-gray-100 bg-white/60 rounded-full pr-6 py-3 focus:ring-4 focus:ring-orange-100 focus:border-orange-500 outline-none transition-all font-medium text-gray-700 placeholder-gray-400 backdrop-blur-sm disabled:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError(''); // Clear error on input
                }}
              />
            </div>
          </div>

          {/* Login Button */}
          <button 
            type="submit"
            disabled={isLoading}
            className="mt-6 w-full bg-orange-600 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-bold py-4 rounded-full shadow-xl shadow-orange-500/40 active:scale-[0.98] transition-all flex items-center justify-center gap-2 text-lg"
          >
            {isLoading ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <Lock className="w-5 h-5" /> 
                <span>Access System</span>
              </>
            )}
          </button>

        </form>
        
        <div className="mt-8 text-center border-t border-gray-100 pt-4">
          <p className="text-xs text-gray-400 font-medium">
            Powered by BakeryOS v1.0 • Secure Login
          </p>
          {/* Development Help Text */}
          {/* <p className="text-[10px] text-gray-300 mt-2 italic">
            Demo: manager/cashier/baker/store • Password: 123
          </p> */}
        </div>
      </div>
    </div>
  );
}