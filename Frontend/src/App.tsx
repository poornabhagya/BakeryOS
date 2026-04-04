import { useState, useEffect } from 'react';
import { AuthProvider, useAuth, UserRole } from './context/AuthContext';
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

type MenuPage =
  | 'dashboard'
  | 'users'
  | 'billing'
  | 'stock'
  | 'wastage'
  | 'saleshistory'
  | 'discount'
  | 'notification';

const PAGE_ACCESS: Record<UserRole, MenuPage[]> = {
  Manager: ['dashboard', 'users', 'billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification'],
  Cashier: ['billing', 'stock', 'wastage', 'saleshistory', 'discount', 'notification'],
  Baker: ['dashboard', 'stock', 'wastage', 'notification'],
  Storekeeper: ['dashboard', 'stock', 'wastage', 'notification'],
};

const ALL_MENU_PAGES: MenuPage[] = [
  'dashboard',
  'users',
  'billing',
  'stock',
  'wastage',
  'saleshistory',
  'discount',
  'notification',
];

const normalizeMenuPage = (value: string): MenuPage | null => {
  return ALL_MENU_PAGES.includes(value as MenuPage) ? (value as MenuPage) : null;
};

const getDefaultPageForRole = (role: UserRole): MenuPage => {
  if (role === 'Cashier') return 'billing';
  return 'dashboard';
};

const canAccessPage = (role: UserRole, page: MenuPage): boolean => {
  return PAGE_ACCESS[role]?.includes(page) ?? false;
};

function BakeryApp() {
  const { user } = useAuth(); 
  const [activeMenuItem, setActiveMenuItem] = useState<MenuPage>('dashboard');

  const setActiveMenuItemIfAllowed = (page: MenuPage) => {
    if (!user) return;
    const role = user.role as UserRole;
    if (canAccessPage(role, page)) {
      setActiveMenuItem(page);
    }
  };

  // --- Smart Redirect Logic ---
  useEffect(() => {
    if (user) {
      const role = user.role as UserRole;
      const defaultPage = getDefaultPageForRole(role);
      setActiveMenuItem(defaultPage);
    }
  }, [user]); // Runs only when 'user' changes (login/logout)

  // Enforce role guard if activeMenuItem is somehow set to an unauthorized page.
  useEffect(() => {
    if (!user) return;
    const role = user.role as UserRole;
    if (!canAccessPage(role, activeMenuItem)) {
      setActiveMenuItem(getDefaultPageForRole(role));
    }
  }, [user, activeMenuItem]);

  // --- Listen for navigation events from dashboard and other components ---
  useEffect(() => {
    const handleNavigate = (event: Event) => {
      if (!user) return;
      const customEvent = event as CustomEvent;
      const requestedPage = normalizeMenuPage(String(customEvent.detail || ''));
      if (!requestedPage) return;

      setActiveMenuItemIfAllowed(requestedPage);
    };

    window.addEventListener('navigate', handleNavigate);
    return () => {
      window.removeEventListener('navigate', handleNavigate);
    };
  }, [user]);

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
        onItemClick={(item) => {
          const normalized = normalizeMenuPage(item);
          if (!normalized) return;
          setActiveMenuItemIfAllowed(normalized);
        }}
        // @ts-ignore
        userRole={user.role} 
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 transition-all duration-300">
        <Header
          breadcrumbPath={getBreadcrumb()}
          onNotificationClick={() => setActiveMenuItemIfAllowed('notification')}
        />
        
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