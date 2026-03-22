import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginScreen } from './components/LoginScreen';

// Components
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { WastageOverview } from './components/WastageOverview';
import { SalesSummary } from './components/SalesSummary';
import { UserManagement } from './components/UserManagement';
import { BillingScreen } from './components/BillingScreen';
import StockManagementScreen from './components/StockManagementScreen';
import DiscountManagement from './components/DiscountManagement';
import { NotificationScreen } from './components/NotificationScreen';

function BakeryApp() {
  const { user } = useAuth(); 
  const [activeMenuItem, setActiveMenuItem] = useState('dashboard');

  // --- Smart Redirect Logic ---
  useEffect(() => {
    if (user) {
      // යූසර් ලොග් වුන ගමන්, එයාගේ රෝල් එක අනුව මුලින්ම යන පිටුව තීරණය කිරීම
      if (user.role === 'Cashier') {
        setActiveMenuItem('billing'); 
      } else if (user.role === 'Baker' || user.role === 'Storekeeper') {
        setActiveMenuItem('stock'); 
      } else {
        setActiveMenuItem('dashboard'); // Manager default
      }
    }
  }, [user]); // Runs only when 'user' changes (login/logout)

  // --- 1. If NO User -> Show Login Screen ---
  if (!user) {
    return <LoginScreen />;
  }

  // --- Breadcrumb Logic ---
  const getBreadcrumb = () => {
    switch (activeMenuItem) {
      case 'users': return ['Dashboard', 'Staff Management'];
      case 'billing': return ['Dashboard', 'Billing'];
      case 'stock': return ['Dashboard', 'Stock Management'];
      case 'wastage': return ['Dashboard', 'Wastage'];
      case 'saleshistory': return ['Dashboard', 'Sales History'];
      case 'discount': return ['Dashboard', 'Discount Management'];
      case 'notification': return ['Dashboard', 'Notifications'];
      default: return ['Dashboard', 'Overview'];
    }
  };

  // --- Content Rendering Logic ---
  const renderContent = () => {
    switch (activeMenuItem) {
      case 'users': return <UserManagement />;
      case 'billing': return <BillingScreen />;
      case 'stock': return <StockManagementScreen />; 
      case 'wastage': return <WastageOverview />;
      case 'saleshistory': return <SalesSummary />;
      case 'discount': return <DiscountManagement />;
      case 'notification': return <NotificationScreen />;
      case 'dashboard':
      default: return <Dashboard />;
    }
  };

  // --- 2. If User Exists -> Show System ---
  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <Sidebar 
        activeItem={activeMenuItem} 
        onItemClick={setActiveMenuItem}
        // @ts-ignore
        userRole={user.role} 
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 transition-all duration-300">
        <Header breadcrumbPath={getBreadcrumb()} />
        
        <main className="p-6">
            {renderContent()}
        </main>
      </div>
    </div>
  );
}

// Wrapper Component
export default function App() {
  return (
    <AuthProvider>
      <BakeryApp />
    </AuthProvider>
  );
}