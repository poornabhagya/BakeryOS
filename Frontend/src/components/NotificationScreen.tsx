import { useState, useEffect, useRef } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Package, Monitor, Lock, MoreVertical, Clock, Check, Trash2, Loader } from 'lucide-react';
import apiClient from '../services/api';

interface Notification {
  id: string;
  type: 'critical' | 'system-open' | 'system-close';
  title: string;
  description: string;
  time: string;
  read: boolean;
}

export function NotificationScreen() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('all');
  const [showSimulatedDropdown, setShowSimulatedDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // --- Fetch Notifications from API ---
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);
        const items = await apiClient.notifications.getAll();
        // items is already a flat array of UI-formatted notifications
        setNotifications(items);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch notifications';
        setFetchError(errorMsg);
        console.error('Error fetching notifications:', error);
        // Fall back to empty array on error
        setNotifications([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNotifications();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowSimulatedDropdown(false);
      }
    };

    if (showSimulatedDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSimulatedDropdown]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return Package;
      case 'system-open':
        return Monitor;
      case 'system-close':
        return Lock;
      default:
        return Package;
    }
  };

  const getIconColor = (type: string) => {
    switch (type) {
      case 'critical':
        return 'bg-red-100 text-red-600';
      case 'system-open':
        return 'bg-green-100 text-green-600';
      case 'system-close':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (activeTab === 'all') return true;
    if (activeTab === 'alerts') return notification.type === 'critical';
    if (activeTab === 'system') return notification.type.startsWith('system');
    return true;
  });

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const markAsResolved = (id: string) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const deleteNotification = (id: string) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  return (
    <div className="p-8">
      <Card className="p-6">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-orange-900 mb-2">Notifications</h1>
            <p className="text-gray-600 text-sm">Stay updated with alerts and system activities</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={markAllAsRead} className="text-orange-700 hover:text-orange-800 hover:bg-orange-50">
              Mark all as read
            </Button>
            <Button variant="outline" onClick={clearAll} className="border-orange-200 text-orange-700 hover:bg-orange-50">
              Clear All
            </Button>
          </div>
        </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList className="bg-orange-50 border border-orange-200 p-1 rounded-lg">
          <TabsTrigger 
            value="all" 
            className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-orange-800 rounded-md px-4 py-2 transition-all"
          >
            All
            <Badge variant="secondary" className="ml-2 bg-orange-100 text-orange-700">
              {notifications.length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="alerts" 
            className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-orange-800 rounded-md px-4 py-2 transition-all"
          >
            Alerts
            <Badge variant="secondary" className="ml-2 bg-red-100 text-red-700">
              {notifications.filter(n => n.type === 'critical').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="system" 
            className="data-[state=active]:bg-orange-600 data-[state=active]:text-white text-orange-800 rounded-md px-4 py-2 transition-all"
          >
            System
            <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-700">
              {notifications.filter(n => n.type.startsWith('system')).length}
            </Badge>
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab}>
          {/* Notification List */}
          <div className="space-y-3">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="flex justify-center mb-4">
                  <Loader className="w-8 h-8 text-orange-600 animate-spin" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Loading notifications</h3>
                <p className="text-gray-600">Please wait...</p>
              </div>
            ) : fetchError ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Package className="w-8 h-8 text-red-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading notifications</h3>
                <p className="text-gray-600">{fetchError}</p>
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Package className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
                <p className="text-gray-600">You're all caught up!</p>
              </div>
            ) : (
              filteredNotifications.map((notification, index) => {
                const Icon = getIcon(notification.type);
                const iconColor = getIconColor(notification.type);
                const isFirst = index === 0 && notification.type === 'critical'; // For the dropdown simulation

                return (
                  <Card 
                    key={notification.id} 
                    className={`p-4 hover:shadow-md transition-all duration-200 cursor-pointer border-l-4 ${
                      notification.read 
                        ? 'bg-white border-l-gray-200 hover:border-l-gray-300' 
                        : 'bg-orange-50 border-l-orange-400 hover:border-l-orange-500'
                    } ${!notification.read ? 'shadow-sm' : ''}`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Icon Badge */}
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${iconColor} shadow-sm`}>
                        <Icon className="w-6 h-6" />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className={`font-semibold text-gray-900 mb-1 ${!notification.read ? 'text-orange-900' : ''}`}>
                              {notification.title}
                            </h3>
                            <p className="text-gray-600 text-sm leading-relaxed mb-2">
                              {notification.description}
                            </p>
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400 text-xs">{notification.time}</span>
                              {!notification.read && (
                                <Badge variant="secondary" className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5">
                                  New
                                </Badge>
                              )}
                            </div>
                          </div>

                          {/* Three-dot Menu - Only show for non-system notifications */}
                          {!notification.type.startsWith('system') && (
                            <div className="relative flex-shrink-0">
                              {isFirst ? (
                                // For first notification, show simulated dropdown
                                <div ref={dropdownRef}>
                                  <Button 
                                    variant="ghost" 
                                    size="icon"
                                    className="h-8 w-8 hover:bg-gray-100"
                                    onClick={() => setShowSimulatedDropdown(!showSimulatedDropdown)}
                                  >
                                    <MoreVertical className="w-4 h-4" />
                                  </Button>
                                  {showSimulatedDropdown && (
                                    <div className="absolute right-0 top-8 z-50 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-1">
                                      <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-900 transition-colors">
                                        <Clock className="w-4 h-4 text-gray-500" />
                                        <span>Snooze (1 Hour)</span>
                                      </button>
                                      <div className="border-t border-gray-100"></div>
                                      <button 
                                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 hover:bg-green-50 hover:text-green-800 transition-colors"
                                        onClick={() => {
                                          markAsResolved(notification.id);
                                          setShowSimulatedDropdown(false);
                                        }}
                                      >
                                        <Check className="w-4 h-4 text-green-600" />
                                        <span>Mark as Resolved</span>
                                      </button>
                                      <div className="border-t border-gray-100"></div>
                                      <button 
                                        className="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors"
                                        onClick={() => {
                                          deleteNotification(notification.id);
                                          setShowSimulatedDropdown(false);
                                        }}
                                      >
                                        <Trash2 className="w-4 h-4 text-red-600" />
                                        <span>Delete</span>
                                      </button>
                                    </div>
                                  )}
                                </div>
                              ) : (
                                // For other notifications, show real dropdown
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-gray-100">
                                      <MoreVertical className="w-4 h-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end" className="w-48">
                                    <DropdownMenuItem>
                                      <Clock className="w-4 h-4 mr-2" />
                                      Snooze (1 Hour)
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => markAsResolved(notification.id)}>
                                      <Check className="w-4 h-4 mr-2" />
                                      Mark as Resolved
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => deleteNotification(notification.id)} className="text-red-600">
                                      <Trash2 className="w-4 h-4 mr-2" />
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })
            )}
          </div>
        </TabsContent>
      </Tabs>
    </Card>
  </div>
);
}