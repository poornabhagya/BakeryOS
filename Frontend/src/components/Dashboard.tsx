import React from 'react';
import { useAuth } from '../context/AuthContext';

// Import the sub-dashboards we just created
import { ManagerDashboard } from './dashboard/ManagerDashboard';
import { BakerDashboard } from './dashboard/BakerDashboard';
import { StorekeeperDashboard } from './dashboard/StorekeeperDashboard';

export function Dashboard() {
  const { user } = useAuth();

  // Role Based Routing Logic
  switch (user?.role) {
    case 'Manager':
      return <ManagerDashboard />;
    
    case 'Baker':
      return <BakerDashboard />;
    
    case 'Storekeeper':
      return <StorekeeperDashboard />;
      
    case 'Cashier':
      // Cashier has no dashboard, show a welcome screen
      return (
        <div className="h-full flex flex-col items-center justify-center p-12 text-center text-gray-500">
          <div className="bg-orange-50 p-6 rounded-full mb-4">
            <span className="text-4xl">👋</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome Back, {user.full_name}!</h2>
          <p className="max-w-md">You are logged in as a Cashier. Please use the <span className="font-bold text-orange-600">Billing Tab</span> in the sidebar to start processing sales.</p>
        </div>
      );

    default:
      return <div className="p-8">Access Denied: Unknown Role</div>;
  }
}