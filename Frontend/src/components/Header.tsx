import { useEffect, useMemo, useState } from 'react';
import { Bell, ChevronRight, User } from 'lucide-react';
import { Badge } from './ui/badge';
import { useAuth } from '../context/AuthContext'; // 1. Imported the context
import apiClient from '../services/api';

interface HeaderProps {
  breadcrumbPath?: string[];
  onNotificationClick?: () => void;
}

export function Header({ breadcrumbPath = ['Dashboard', 'Overview'], onNotificationClick }: HeaderProps) {
  const { user } = useAuth(); // 2. Got details of the logged-in user
  const [unreadCount, setUnreadCount] = useState(0);
  const displayName = user?.name || user?.username || (user as any)?.first_name || 'User';

  const fetchUnreadCount = async () => {
    try {
      const notifications = await apiClient.notifications.getAll();
      const unread = (notifications || []).filter((notification: any) => {
        const isUnreadByFlag = notification?.is_read === false || notification?.read === false;
        const status = String(notification?.status || '').toLowerCase();
        const isUnreadByStatus = status === 'unread';
        return isUnreadByFlag || isUnreadByStatus;
      }).length;
      setUnreadCount(unread);
    } catch (error) {
      console.error('Failed to fetch unread notifications for header:', error);
      setUnreadCount(0);
    }
  };

  useEffect(() => {
    fetchUnreadCount();
    const intervalId = window.setInterval(fetchUnreadCount, 60000);
    return () => window.clearInterval(intervalId);
  }, []);

  const unreadBadge = useMemo(() => {
    if (unreadCount <= 0) return null;
    return unreadCount > 99 ? '99+' : String(unreadCount);
  }, [unreadCount]);

  // 3. Access Level Text shown below according to Role
  const getAccessLevel = (role?: string) => {
    switch (role) {
      case 'Manager': return 'Admin Access';
      case 'Cashier': return 'Billing Portal';
      case 'Baker': return 'Production Access';
      case 'Storekeeper': return 'Inventory Access';
      default: return 'Staff Access';
    }
  };

  // 4. Avatar Background Color by Role (Safe Colors)
  const getAvatarColor = (role?: string) => {
    switch (role) {
      case 'Manager': return 'bg-gradient-to-br from-orange-500 to-orange-700'; // Let's give the Manager the same old Gradient
      case 'Cashier': return 'bg-green-600';
      case 'Baker': return 'bg-yellow-600';
      case 'Storekeeper': return 'bg-blue-600';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span className="text-orange-700 font-medium">{breadcrumbPath[0]}</span>
        <ChevronRight className="w-4 h-4 text-gray-400" />
        <span className="font-medium text-gray-900">{breadcrumbPath[1]}</span>
      </div>

      {/* Right Side: Notification & User Profile */}
      <div className="flex items-center gap-4">
        {/* Notification Bell */}
        <button
          onClick={onNotificationClick}
          className="relative p-2 hover:bg-gray-100 rounded-full transition-colors group"
          aria-label="Open notifications"
          title="Notifications"
        >
          <Bell className="w-5 h-5 text-gray-600 group-hover:text-orange-600 transition-colors" />
          {unreadBadge && (
            <Badge className="absolute top-1 right-1 bg-orange-600 text-white border-2 border-white px-1.5 py-0.5 text-[10px] min-w-[18px] h-[18px] flex items-center justify-center">
              {unreadBadge}
            </Badge>
          )}
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <div className="text-right hidden md:block">
            {/* User's Name */}
            <p className="text-sm font-bold text-gray-900 leading-none mb-1">
              {displayName}
            </p>
            {/* Access Level corresponding to the user's role */}
            <p className="text-xs text-gray-500 font-medium">
              {getAccessLevel(user?.role)}
            </p>
          </div>
          
          {/* Avatar Icon */}
          <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-sm border-2 border-white ring-1 ring-gray-100 ${getAvatarColor(user?.role)}`}>
            <User className="w-5 h-5 text-white" />
          </div>
        </div>
      </div>
    </div>
  );
}