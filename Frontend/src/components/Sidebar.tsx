import { 
  LayoutDashboard, 
  Receipt,
  Package, 
  AlertTriangle, 
  History,
  Percent,
  Bell,
  Users,
  LogOut // 1. Logout Icon added
} from 'lucide-react';
import { useAuth } from '../context/AuthContext'; // 2. Imported the context to get the Logout function

interface SidebarProps {
  activeItem: string;
  onItemClick: (item: string) => void;
  userRole: string; // 3. Added userRole to Props
}

// 4. We assign roles according to the Access Plan we created.
const menuItems = [
  { 
    id: 'dashboard', 
    label: 'Dashboard', 
    icon: LayoutDashboard, 
    roles: ['Manager', 'Baker', 'Storekeeper'] // Cashier does not see Dashboard
  },
  { 
    id: 'billing', 
    label: 'Billing', 
    icon: Receipt, 
    roles: ['Manager', 'Cashier'] 
  },
  { 
    id: 'stock', 
    label: 'Stock', 
    icon: Package, 
    roles: ['Manager', 'Baker', 'Storekeeper', 'Cashier'] // Cashier can view only
  },
  { 
    id: 'wastage', 
    label: 'Wastage', 
    icon: AlertTriangle, 
    roles: ['Manager', 'Baker', 'Storekeeper', 'Cashier'] 
  },
  { 
    id: 'saleshistory', 
    label: 'Sales History', 
    icon: History, 
    roles: ['Manager', 'Cashier'] 
  },
  { 
    id: 'discount', 
    label: 'Discount', 
    icon: Percent, 
    roles: ['Manager', 'Cashier'] 
  },
  { 
    id: 'notification', 
    label: 'Notification', 
    icon: Bell, 
    roles: ['Manager', 'Cashier', 'Baker', 'Storekeeper'] // For everyone
  },
  { 
    id: 'users', 
    label: 'Users', 
    icon: Users, 
    roles: ['Manager'] // Only for Manager
  },
];

export function Sidebar({ activeItem, onItemClick, userRole }: SidebarProps) {
  const { logout } = useAuth(); // Using the Logout hook

  return (
    // 'flex flex-col' added to create the bottom logout
    <div className="w-64 h-screen bg-gradient-to-b from-orange-50 to-orange-100 border-r border-orange-200 fixed left-0 top-0 flex flex-col">
      
      {/* Branding */}
      <div className="p-6 border-b border-orange-200">
        <h1 className="text-orange-900 flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-700 rounded-xl flex items-center justify-center">
            <span className="text-xl">🥖</span>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg leading-tight">BakeryOS</span>
            {/* Role Badge - Shows who is logged in */}
            <span className="text-[10px] uppercase tracking-wider text-orange-500 font-semibold">
              {userRole} Portal
            </span>
          </div>
        </h1>
      </div>

      {/* Menu Items (flex-1 takes up all the remaining space) */}
      <nav className="p-4 space-y-1 flex-1 overflow-y-auto">
        {menuItems.map((item) => {
          
          // 5. Filtering Logic: If the role does not match, the button will not be created.
          if (!item.roles.includes(userRole)) {
            return null;
          }

          const Icon = item.icon;
          const isActive = activeItem === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onItemClick(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all font-medium ${
                isActive
                  ? 'bg-orange-600 text-white shadow-md'
                  : 'text-orange-800 hover:bg-orange-200'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* 6. Logout Button (Scroll down) */}
      <div className="p-4 border-t border-orange-200">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 hover:bg-red-50 hover:shadow-sm transition-all font-medium group"
        >
          <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
}