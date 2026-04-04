import { useState, useEffect, useCallback } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from './ui/dropdown-menu';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Package, Monitor, Lock, MoreVertical, Clock, Check, Trash2, Loader, FileText, FileSpreadsheet } from 'lucide-react';
import apiClient from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Notification {
  id: string | number;
  type: string; // Backend types: LowStock, Expiry, HighWastage, OutOfStock, System, Warning, etc.
  title: string;
  message: string;
  created_at: string;
  read: boolean;
  status: 'unread' | 'read' | 'snoozed' | 'archived';
}

export function NotificationScreen() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('all');
  const [toast, setToast] = useState<{ visible: boolean; type: 'success' | 'error'; message: string }>({
    visible: false,
    type: 'success',
    message: '',
  });

  const fetchNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      setFetchError(null);
      const items = await apiClient.notifications.getAll();
      const notificationsWithStatus: Notification[] = items.map((notification: any) => {
        const isRead = notification.is_read ?? notification.read ?? false;
        return {
          id: notification.id,
          type: notification.type,
          title: notification.title,
          message: notification.message ?? notification.description ?? '',
          created_at: notification.created_at ?? notification.time ?? '',
          read: isRead,
          status: notification.status || (isRead ? 'read' : 'unread'),
        };
      });
      setNotifications(notificationsWithStatus);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to fetch notifications';
      setFetchError(errorMsg);
      console.error('Error fetching notifications:', error);
      // Fall back to empty array on error
      setNotifications([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // --- Fetch Notifications from API ---
  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const getNotificationTypeLabel = (type: string): string => {
    switch (type) {
      case 'OutOfStock':
        return 'Out of Stock';
      case 'LowStock':
        return 'Low Stock';
      case 'Expiry':
        return 'Expiry Alert';
      case 'HighWastage':
        return 'High Wastage';
      case 'Warning':
        return 'Warning';
      case 'System':
        return 'System';
      default:
        return type;
    }
  };

  const categorizeNotification = (type: string): 'Alert' | 'System' => {
    const alertTypes = ['OutOfStock', 'LowStock', 'Expiry', 'HighWastage'];
    return alertTypes.includes(type) ? 'Alert' : 'System';
  };

  const getIcon = (type: string) => {
    const category = categorizeNotification(type);
    if (category === 'Alert') {
      return Package;
    } else {
      return Monitor;
    }
  };

  const getIconColor = (type: string) => {
    const category = categorizeNotification(type);
    if (category === 'Alert') {
      return 'bg-red-100 text-red-600';
    } else {
      return 'bg-blue-100 text-blue-600';
    }
  };

  const filteredNotifications = notifications
    .filter(notification => notification.status !== 'archived')
    .filter(notification => {
      if (activeTab === 'all') return true;
      if (activeTab === 'unread') return notification.status === 'unread';
      if (activeTab === 'read') return notification.status === 'read';
      if (activeTab === 'alert') return categorizeNotification(notification.type) === 'Alert';
      if (activeTab === 'system') return categorizeNotification(notification.type) === 'System';
      return true;
    });

  const markAsRead = async (id: string | number) => {
    try {
      console.log(`[NotificationScreen] Marking notification ${id} as read`);
      
      // Update local state immediately
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, read: true, status: 'read' as const } : n
      ));

      // Make API PATCH request
      await apiClient.notifications.update(id, { status: 'read' });
      
      console.log(`[NotificationScreen] Notification ${id} marked as read successfully`);
    } catch (error) {
      console.error('[NotificationScreen] Error marking notification as read:', error);
      // Revert on failure (optional)
    }
  };

  const snoozeNotification = async (id: string | number) => {
    try {
      console.log(`[NotificationScreen] Snoozing notification ${id}`);
      
      // Update local state immediately
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, status: 'snoozed' as const } : n
      ));

      // Make API PATCH request
      await apiClient.notifications.update(String(id), { status: 'snoozed' });
      
      console.log(`[NotificationScreen] Notification ${id} snoozed successfully`);
    } catch (error) {
      console.error('[NotificationScreen] Error snoozing notification:', error);
      // Revert on failure (optional)
    }
  };

  const deleteNotification = async (id: string | number) => {
    try {
      console.log(`[NotificationScreen] Archiving notification ${id}`);
      
      // Update local state immediately
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, status: 'archived' as const } : n
      ));

      // Make API PATCH request
      await apiClient.notifications.update(String(id), { status: 'archived' });
      
      console.log(`[NotificationScreen] Notification ${id} archived successfully`);
    } catch (error) {
      console.error('[NotificationScreen] Error archiving notification:', error);
      // Revert on failure (optional)
    }
  };

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ visible: true, type, message });
    setTimeout(() => setToast((prev) => ({ ...prev, visible: false })), 5000);
  };

  const handleCounterReportExport = async (notification: Notification, format: 'pdf' | 'excel') => {
    try {
      const download = format === 'pdf'
        ? apiClient.notifications.downloadCounterReportPdf
        : apiClient.notifications.downloadCounterReportExcel;

      const { blob, fileName } = await download(notification.id);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);

      // Backend marks this notification as read; refresh list to reflect dimmed/read state.
      await fetchNotifications();

      showToast(
        format === 'pdf'
          ? 'Shift report PDF downloaded successfully.'
          : 'Shift report Excel downloaded successfully.',
        'success'
      );
    } catch (error: any) {
      showToast(
        error?.message || (format === 'pdf' ? 'Failed to download shift report PDF.' : 'Failed to download shift report Excel.'),
        'error'
      );
    }
  };

  return (
    <div className="p-8">
      {toast.visible && (
        <div className="fixed top-6 right-6 z-[80] w-[420px] max-w-[calc(100vw-3rem)]">
          <div className={`rounded-xl border bg-white px-4 py-3 shadow-2xl ${
            toast.type === 'success' ? 'border-green-300' : 'border-red-300'
          }`}>
            <div className={`text-sm font-semibold ${toast.type === 'success' ? 'text-green-700' : 'text-red-700'}`}>
              {toast.type === 'success' ? 'Done' : 'Access Restricted'}
            </div>
            <div className="mt-1 text-sm text-slate-800">{toast.message}</div>
          </div>
        </div>
      )}
      <Card className="p-6">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-orange-900 mb-2">Notifications</h1>
            <p className="text-gray-600 text-sm">Stay updated with alerts and system activities</p>
          </div>
        </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList className="bg-orange-50 border border-orange-200 p-1 rounded-lg flex flex-wrap">
          <TabsTrigger 
            value="all" 
            className={`rounded-md px-4 py-2 transition-all ${activeTab === 'all' ? 'bg-white border border-orange-200 shadow-md text-orange-900' : 'bg-transparent text-orange-700 text-orange-900'}`}
          >
            All
            <Badge variant="secondary" className="ml-2 bg-orange-100 text-orange-700">
              {notifications.filter(n => n.status !== 'archived').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="unread" 
            className={`rounded-md px-4 py-2 transition-all ${activeTab === 'unread' ? 'bg-white border border-orange-200 shadow-md text-orange-900' : 'bg-transparent text-orange-700 text-orange-900'}`}
          >
            Unread
            <Badge variant="secondary" className="ml-2 bg-yellow-100 text-yellow-700">
              {notifications.filter(n => n.status === 'unread' && n.status !== 'archived').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="read" 
            className={`rounded-md px-4 py-2 transition-all ${activeTab === 'read' ? 'bg-white border border-orange-200 shadow-md text-orange-900' : 'bg-transparent text-orange-700 text-orange-900'}`}
          >
            Read
            <Badge variant="secondary" className="ml-2 bg-green-100 text-green-700">
              {notifications.filter(n => n.status === 'read' && n.status !== 'archived').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="alert" 
            className={`rounded-md px-4 py-2 transition-all ${activeTab === 'alert' ? 'bg-white border border-orange-200 shadow-md text-orange-900' : 'bg-transparent text-orange-700 text-orange-900'}`}
          >
            Alert
            <Badge variant="secondary" className="ml-2 bg-red-100 text-red-700">
              {notifications.filter(n => categorizeNotification(n.type) === 'Alert' && n.status !== 'archived').length}
            </Badge>
          </TabsTrigger>
          <TabsTrigger 
            value="system" 
            className={`rounded-md px-4 py-2 transition-all ${activeTab === 'system' ? 'bg-white border border-orange-200 shadow-md text-orange-900' : 'bg-transparent text-orange-700 text-orange-900'}`}
          >
            System
            <Badge variant="secondary" className="ml-2 bg-blue-100 text-blue-700">
              {notifications.filter(n => categorizeNotification(n.type) === 'System' && n.status !== 'archived').length}
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
              filteredNotifications.map((notification) => {
                const Icon = getIcon(notification.type);
                const iconColor = getIconColor(notification.type);
                const isSystemNotification = notification.type === 'System';
                const isCounterStatusNotification = notification.type === 'System' && notification.title === 'Counter Status Update';
                const isManager = user?.role === 'Manager';

                return (
                  <Card 
                    key={notification.id} 
                    className={`p-4 hover:shadow-md transition-all duration-200 cursor-pointer border-l-4 ${
                      notification.status === 'read'
                        ? 'bg-white border-l-gray-200 hover:border-l-gray-300' 
                        : 'bg-orange-50 border-l-orange-400 hover:border-l-orange-500'
                    } ${notification.status !== 'read' ? 'shadow-sm' : ''}`}
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
                            <p className="text-gray-600 text-sm leading-relaxed mb-2 whitespace-pre-wrap">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400 text-xs">
                                {notification.created_at ? new Date(notification.created_at).toLocaleString() : ''}
                              </span>
                              {!notification.read && (
                                <Badge variant="secondary" className="bg-orange-100 text-orange-700 text-xs px-2 py-0.5">
                                  New
                                </Badge>
                              )}
                              {/* Status Badge */}
                              <Badge 
                                variant="secondary" 
                                className={`text-xs px-2 py-0.5 ${
                                  notification.status === 'read' 
                                    ? 'bg-green-100 text-green-700' 
                                    : notification.status === 'snoozed'
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'bg-gray-100 text-gray-700'
                                }`}
                              >
                                {notification.status.charAt(0).toUpperCase() + notification.status.slice(1)}
                              </Badge>
                              {/* Notification Type Badge */}
                              <Badge 
                                variant="secondary" 
                                className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700"
                              >
                                {getNotificationTypeLabel(notification.type)}
                              </Badge>
                            </div>
                          </div>

                          {/* Three-dot Menu - available for all notifications. */}
                          <div className="relative flex-shrink-0">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 hover:bg-gray-100"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <MoreVertical className="w-4 h-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent
                                align="end"
                                className="w-48 bg-white border-gray-200"
                                onClick={(e) => e.stopPropagation()}
                              >
                                {!isSystemNotification && (
                                  <DropdownMenuItem onClick={() => snoozeNotification(notification.id)}>
                                    <Clock className="w-4 h-4 mr-2" />
                                    Snooze (1 Hour)
                                  </DropdownMenuItem>
                                )}
                                  {isCounterStatusNotification && isManager ? (
                                    <>
                                      <DropdownMenuItem onClick={() => handleCounterReportExport(notification, 'pdf')}>
                                        <FileText className="w-4 h-4 mr-2" />
                                        Export PDF
                                      </DropdownMenuItem>
                                      <DropdownMenuItem onClick={() => handleCounterReportExport(notification, 'excel')}>
                                        <FileSpreadsheet className="w-4 h-4 mr-2" />
                                        Export Excel
                                      </DropdownMenuItem>
                                    </>
                                  ) : (
                                    <DropdownMenuItem onClick={() => markAsRead(notification.id)}>
                                      <Check className="w-4 h-4 mr-2" />
                                      Mark as Read
                                    </DropdownMenuItem>
                                  )}
                                {!isSystemNotification && (
                                  <DropdownMenuItem onClick={() => deleteNotification(notification.id)} className="text-red-600">
                                    <Trash2 className="w-4 h-4 mr-2" />
                                    Delete
                                  </DropdownMenuItem>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
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