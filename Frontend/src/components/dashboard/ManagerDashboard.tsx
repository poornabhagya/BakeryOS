import React, { useState, useEffect } from 'react';
import { DollarSign, AlertTriangle, TrendingUp, ShoppingCart, Star, Flame, Clock, Eye, Package, ArrowRight, AlertCircle } from 'lucide-react';
import { analyticsApi } from '../../services/api';
import { inventoryApi } from '../../services/api';

export function ManagerDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sales & Revenue Data
  const [salesStats, setSalesStats] = useState<any>({
    total_revenue: 0,
    total_wastage_loss: 0,
    net_profit: 0,
    total_orders: 0,
  });

  // Product Stats (top selling items)
  const [productStats, setProductStats] = useState<any>({
    top_products: [],
  });

  // Wastage Stats
  const [wastageStats, setWastageStats] = useState<any>({
    breakdown: [],
  });

  // Low Stock Alerts
  const [lowStockItems, setLowStockItems] = useState<any[]>([]);

  // Recent Transactions (derived from sales)
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch all analytics in parallel
        const [salesData, productData, wastageData, lowStockData] = await Promise.all([
          analyticsApi.getSalesStats(),
          analyticsApi.getProductStats(),
          analyticsApi.getWastageStats(),
          inventoryApi.getLowStock(),
        ]);

        // Process Sales Stats
        setSalesStats({
          total_revenue: salesData?.total_revenue || 0,
          total_wastage_loss: salesData?.total_wastage_loss || 0,
          net_profit: (salesData?.total_revenue || 0) - (salesData?.total_wastage_loss || 0),
          total_orders: salesData?.total_orders || 0,
        });

        // Process Product Stats (top selling items)
        const topProducts = productData?.top_products || [];
        setProductStats({
          top_products: topProducts.slice(0, 5),
        });

        // Process Wastage Stats (breakdown by reason)
        const wastageBreakdown = wastageData?.breakdown || [];
        setWastageStats({
          breakdown: wastageBreakdown.slice(0, 4),
        });

        // Process Low Stock Items
        const lowStock = Array.isArray(lowStockData) 
          ? lowStockData.slice(0, 5).map((item: any) => ({
              name: item.name || item.product_name || 'Unknown',
              qty: item.current_stock || 0,
              status: item.current_stock <= 5 ? 'Critical' : 'Low',
            }))
          : [];
        setLowStockItems(lowStock);

        // Recent transactions - no data available since database is empty
        setRecentTransactions([]);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);
  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mb-4 mx-auto w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center gap-3 p-4 rounded-lg bg-red-50 border border-red-200">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* ROW 1: KEY METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-green-50 border border-green-200">
          <div className="p-3 rounded bg-white text-green-600">
            <DollarSign className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-green-800 font-semibold">Total Revenue</div>
            <div className="text-lg font-bold text-green-700">Rs. {(salesStats.total_revenue || 0).toLocaleString()}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Total Wastage Loss</div>
            <div className="text-lg font-bold text-red-700">Rs. {(salesStats.total_wastage_loss || 0).toLocaleString()}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
          <div className="p-3 rounded bg-white text-blue-600">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-blue-800 font-semibold">Net Profit</div>
            <div className="text-lg font-bold text-blue-700">Rs. {(salesStats.net_profit || 0).toLocaleString()}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <ShoppingCart className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Total Orders</div>
            <div className="text-lg font-bold text-orange-700">{salesStats.total_orders || 0}</div>
          </div>
        </div>
      </div>

      {/* ROW 2: PERFORMANCE LISTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">Top Selling Items (Today)</h3>
          </div>
          <div className="space-y-3">
            {productStats.top_products.length > 0 ? (
              productStats.top_products.map((item: any, index: number) => (
                <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                  <span className="text-gray-800 font-medium">{item.product_name || 'Unknown'}</span>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>{item.quantity_sold || 0} pcs</span>
                    <span className="font-semibold text-gray-800">Rs. {(item.total_sales || 0).toLocaleString()}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No data available</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Flame className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-800">Wastage Breakdown</h3>
          </div>
          <div className="space-y-3">
            {wastageStats.breakdown.length > 0 ? (
              wastageStats.breakdown.map((item: any, index: number) => {
                const getBadgeColor = (reason: string) => {
                  const colors: Record<string, string> = {
                    'Expired': 'bg-red-100 text-red-700',
                    'Burnt': 'bg-orange-100 text-orange-700',
                    'Damaged': 'bg-yellow-100 text-yellow-700',
                    'Spilled': 'bg-blue-100 text-blue-700',
                  };
                  return colors[reason] || 'bg-gray-100 text-gray-700';
                };
                return (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getBadgeColor(item.reason)}`}>
                      {item.reason}
                    </span>
                    <span className="font-semibold text-gray-800">Rs. {(item.total_loss || 0).toLocaleString()}</span>
                  </div>
                );
              })
            ) : (
              <p className="text-gray-500 text-center py-4">No wastage data</p>
            )}
          </div>
        </div>
      </div>

      {/* ROW 3: OPERATIONAL DATA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-800">Recent Transactions</h3>
            </div>
            <button className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1">
              View All History <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Bill ID</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Time</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Amount</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.length > 0 ? (
                  recentTransactions.map((transaction, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{transaction.id}</td>
                      <td className="py-2 px-2 text-gray-600">{transaction.time}</td>
                      <td className="py-2 px-2 text-gray-800 font-semibold">Rs. {transaction.amount.toLocaleString()}</td>
                      <td className="py-2 px-2">
                        <button className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1">
                          <Eye className="w-4 h-4" /> View
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="py-4 text-center text-gray-500">No recent transactions</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-semibold text-gray-800">Low Stock Alerts</h3>
            </div>
            <button className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1">
              View Inventory <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Item Name</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Remaining Qty</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {lowStockItems.length > 0 ? (
                  lowStockItems.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                      <td className="py-2 px-2 text-gray-600">{item.qty} pcs</td>
                      <td className="py-2 px-2 text-red-600 font-semibold">{item.status}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="py-4 text-center text-gray-500">No low stock items</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}