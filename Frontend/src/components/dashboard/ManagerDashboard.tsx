import React, { useState, useEffect, useRef } from 'react';
import { DollarSign, AlertTriangle, TrendingUp, ShoppingCart, Star, Flame, Clock, Eye, Package, ArrowRight, AlertCircle, Loader, ChevronDown, Download } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { analyticsApi, inventoryApi, saleApi, wastageApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export function ManagerDashboard() {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showExportDropdown, setShowExportDropdown] = useState(false);
  const [isExportingExcel, setIsExportingExcel] = useState(false);
  const exportDropdownRef = useRef<HTMLDivElement | null>(null);

  // Navigation helper - emits event to parent App component
  const navigateTo = (page: string) => {
    // Dispatch custom event that App.tsx listens to
    window.dispatchEvent(new CustomEvent('navigate', { detail: page }));
  };

  // Global Date Filter (for KPIs, Top Selling Items, Wastage Breakdown)
  const [globalDateFilter, setGlobalDateFilter] = useState<'Today' | 'This Week' | 'This Month'>('Today');

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

  // Wastage Stats (separated by type)
  const [wastageStats, setWastageStats] = useState<any>({
    productBreakdown: [],
    ingredientBreakdown: [],
    isLoading: true,
  });

  // Low Stock Alerts
  const [lowStockItems, setLowStockItems] = useState<any[]>([]);

  // Recent Transactions (derived from sales)
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);

  const canExportSummary = user?.role === 'Manager';

  // Helper function to get date range based on globalDateFilter
  const getDateRange = () => {
    const today = new Date();
    let dateFrom = new Date();

    if (globalDateFilter === 'Today') {
      dateFrom = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    } else if (globalDateFilter === 'This Week') {
      const day = today.getDay();
      const diff = today.getDate() - day + (day === 0 ? -6 : 1);
      dateFrom = new Date(today.getFullYear(), today.getMonth(), diff);
    } else if (globalDateFilter === 'This Month') {
      dateFrom = new Date(today.getFullYear(), today.getMonth(), 1);
    }

    return {
      dateFrom: dateFrom.toISOString().slice(0, 10),
      dateTo: today.toISOString().slice(0, 10),
    };
  };

  const exportToPDF = () => {
    const pdf = new jsPDF();
    const margin = 14;
    let currentY = 18;

    pdf.setFontSize(18);
    pdf.setTextColor(0, 100, 0);
    pdf.text('BakeryOS - Dashboard Summary', margin, currentY);
    currentY += 8;

    pdf.setFontSize(10);
    pdf.setTextColor(90, 90, 90);
    pdf.text(
      `Generated: ${new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      })}`,
      margin,
      currentY
    );
    currentY += 6;

    pdf.text(`Time Period: ${globalDateFilter}`, margin, currentY);
    currentY += 8;

    autoTable(pdf, {
      startY: currentY,
      head: [['KPI', 'Value']],
      body: [
        ['Total Revenue', `Rs. ${(salesStats.total_revenue || 0).toLocaleString()}`],
        ['Total Wastage Loss', `Rs. ${(salesStats.total_wastage_loss || 0).toLocaleString()}`],
        ['Net Profit', `Rs. ${(salesStats.net_profit || 0).toLocaleString()}`],
        ['Total Orders', `${salesStats.total_orders || 0}`],
      ],
      headStyles: {
        fillColor: [0, 100, 0],
        textColor: [255, 255, 255],
        fontStyle: 'bold',
      },
      bodyStyles: {
        textColor: [40, 40, 40],
      },
      margin: { left: margin, right: margin },
    });

    const timestamp = new Date().toISOString().slice(0, 10);
    pdf.save(`dashboard_summary_${globalDateFilter.toLowerCase().replace(/\s+/g, '_')}_${timestamp}.pdf`);
  };

  const exportToExcel = async () => {
    try {
      setIsExportingExcel(true);
      const { blob, fileName } = await analyticsApi.exportDashboardSummaryExcel(globalDateFilter);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('[ManagerDashboard] Failed to export summary Excel:', err);
      alert('Failed to export Excel summary');
    } finally {
      setIsExportingExcel(false);
      setShowExportDropdown(false);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!showExportDropdown) {
        return;
      }

      if (
        exportDropdownRef.current &&
        !exportDropdownRef.current.contains(event.target as Node)
      ) {
        setShowExportDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showExportDropdown]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Get date range based on global filter
        const { dateFrom, dateTo } = getDateRange();

        // Fetch all analytics in parallel
        // NOTE: Low Stock and Recent Transactions are fetched WITHOUT date filtering
        const [salesData, productData, lowStockData, salesList, wastageData] = await Promise.all([
          analyticsApi.getSalesStats(dateFrom, dateTo), // Apply date filter
          analyticsApi.getProductStats(), // TODO: Update backend to support date params
          inventoryApi.getLowStock(), // NO filtering - always latest stock
          saleApi.getAll(), // NO filtering - always latest transactions
          wastageApi.getAll(), // Will be filtered client-side
        ]);

        // Process Sales Stats (with date filtering applied)
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

        // Process Wastage Stats (group by reason for products and ingredients separately)
        const wastageItems = wastageData?.items || [];
        
        // Filter wastage items by date range (client-side filtering)
        const filteredWastageItems = wastageItems.filter((item: any) => {
          const itemDate = item.created_at?.split('T')[0]; // Extract YYYY-MM-DD
          return itemDate >= dateFrom && itemDate <= dateTo;
        });
        
        // Separate products and ingredients
        const productWastage = filteredWastageItems.filter((item: any) => item.wastage_id?.startsWith('PW'));
        const ingredientWastage = filteredWastageItems.filter((item: any) => item.wastage_id?.startsWith('IW'));
        
        // Group products by reason
        const productMapByReason = new Map<string, number>();
        productWastage.forEach((item: any) => {
          const reason = item.reason_text || 'Unknown';
          const loss = item.unit_cost ? Number(item.unit_cost) * Number(item.quantity) : 0;
          productMapByReason.set(reason, (productMapByReason.get(reason) || 0) + loss);
        });
        
        // Group ingredients by reason
        const ingredientMapByReason = new Map<string, number>();
        ingredientWastage.forEach((item: any) => {
          const reason = item.reason_text || 'Unknown';
          const loss = item.unit_cost ? Number(item.unit_cost) * Number(item.quantity) : 0;
          ingredientMapByReason.set(reason, (ingredientMapByReason.get(reason) || 0) + loss);
        });
        
        // Convert to sorted arrays and take top 5
        const productBreakdown = Array.from(productMapByReason.entries())
          .map(([reason, total_loss]) => ({ reason, total_loss }))
          .sort((a, b) => b.total_loss - a.total_loss)
          .slice(0, 5);
        
        const ingredientBreakdown = Array.from(ingredientMapByReason.entries())
          .map(([reason, total_loss]) => ({ reason, total_loss }))
          .sort((a, b) => b.total_loss - a.total_loss)
          .slice(0, 5);
        
        setWastageStats({
          productBreakdown,
          ingredientBreakdown,
          isLoading: false,
        });

        // Process Low Stock Items (NO filtering - always show latest)
        const lowStock = Array.isArray(lowStockData) 
          ? lowStockData.slice(0, 5).map((item: any) => ({
              name: item.name || item.product_name || 'Unknown',
              qty: item.current_stock || 0,
              status: item.current_stock <= 5 ? 'Critical' : 'Low',
            }))
          : [];
        setLowStockItems(lowStock);

        // Process Recent Transactions from sales list
        const transactions = (salesList?.items || [])
          .slice(0, 5) // Get last 5 transactions
          .map((sale: any) => ({
            id: sale.bill_number || `BILL-${sale.id}`,
            time: new Date(sale.created_at).toLocaleString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              hour: '2-digit', 
              minute: '2-digit' 
            }),
            amount: parseFloat(sale.total_amount || sale.total || 0),
          }));
        setRecentTransactions(transactions);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [globalDateFilter]);
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
      {/* GLOBAL DATE FILTER */}
      <div className="flex items-center gap-4 bg-white rounded-lg shadow-sm p-4">
        <label className="text-sm font-semibold text-gray-700">Filter by:</label>
        <select
          value={globalDateFilter}
          onChange={(e) => setGlobalDateFilter(e.target.value as 'Today' | 'This Week' | 'This Month')}
          className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-gray-800 font-medium hover:bg-orange-100 transition-colors cursor-pointer"
        >
          <option value="Today">Today</option>
          <option value="This Week">This Week</option>
          <option value="This Month">This Month</option>
        </select>
        {canExportSummary && (
          <div ref={exportDropdownRef} className="relative">
            <button
              onClick={() => setShowExportDropdown((prev) => !prev)}
              className="px-4 py-2 rounded-lg border border-orange-300 bg-white text-orange-700 font-semibold hover:bg-orange-50 flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export Summary Report
              <ChevronDown className="w-4 h-4" />
            </button>
            {showExportDropdown && (
              <div className="absolute top-full mt-2 left-0 w-48 bg-white border border-orange-100 rounded-lg shadow-lg z-20 overflow-hidden">
                <button
                  onClick={() => {
                    exportToPDF();
                    setShowExportDropdown(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 transition-colors"
                >
                  Export PDF
                </button>
                <button
                  onClick={exportToExcel}
                  disabled={isExportingExcel}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 transition-colors disabled:opacity-60"
                >
                  {isExportingExcel ? 'Exporting Excel...' : 'Export Excel'}
                </button>
              </div>
            )}
          </div>
        )}
        <span className="text-xs text-gray-500 ml-auto">
          Applies to: KPIs, Top Selling Items, Wastage Breakdown
        </span>
      </div>

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
            <h3 className="text-lg font-semibold text-gray-800">Top Selling Items</h3>
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
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-semibold text-gray-800">Wastage Breakdown</h3>
            </div>
            <button
              onClick={() => navigateTo('wastage')}
              className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1 transition-colors"
            >
              Full wastage details <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {wastageStats.isLoading ? (
            <div className="flex items-center justify-center py-8 text-gray-500">
              <Loader className="w-5 h-5 animate-spin mr-2" />
              Loading wastage data...
            </div>
          ) : wastageStats.productBreakdown.length === 0 && wastageStats.ingredientBreakdown.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No wastage data</p>
          ) : (
            <div className="space-y-6">
              {/* Product Wastage Section */}
              {wastageStats.productBreakdown.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b border-orange-200">
                    Product Wastage
                  </h4>
                  <div className="space-y-2">
                    {wastageStats.productBreakdown.map((item: any, index: number) => {
                      const getBadgeColor = (reason: string) => {
                        const colors: Record<string, string> = {
                          'Expired': 'bg-red-100 text-red-700',
                          'Burnt': 'bg-orange-100 text-orange-700',
                          'Damaged': 'bg-yellow-100 text-yellow-700',
                          'Spilled': 'bg-blue-100 text-blue-700',
                          'Stale': 'bg-gray-100 text-gray-700',
                        };
                        return colors[reason] || 'bg-gray-100 text-gray-700';
                      };
                      return (
                        <div
                          key={index}
                          className="flex items-center justify-between py-1 px-2 rounded hover:bg-orange-50 transition-colors"
                        >
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getBadgeColor(item.reason)}`}>
                            {item.reason}
                          </span>
                          <span className="font-semibold text-gray-800 text-sm">
                            Rs. {(item.total_loss || 0).toLocaleString()}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Ingredient Wastage Section */}
              {wastageStats.ingredientBreakdown.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 pb-2 border-b border-blue-200">
                    Ingredient Wastage
                  </h4>
                  <div className="space-y-2">
                    {wastageStats.ingredientBreakdown.map((item: any, index: number) => {
                      const getBadgeColor = (reason: string) => {
                        const colors: Record<string, string> = {
                          'Expired': 'bg-red-100 text-red-700',
                          'Burnt': 'bg-orange-100 text-orange-700',
                          'Damaged': 'bg-yellow-100 text-yellow-700',
                          'Spilled': 'bg-blue-100 text-blue-700',
                          'Stale': 'bg-gray-100 text-gray-700',
                        };
                        return colors[reason] || 'bg-gray-100 text-gray-700';
                      };
                      return (
                        <div
                          key={index}
                          className="flex items-center justify-between py-1 px-2 rounded hover:bg-blue-50 transition-colors"
                        >
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getBadgeColor(item.reason)}`}>
                            {item.reason}
                          </span>
                          <span className="font-semibold text-gray-800 text-sm">
                            Rs. {(item.total_loss || 0).toLocaleString()}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
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
            <button
              onClick={() => navigateTo('saleshistory')}
              className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1 transition-colors"
            >
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
          <div className="flex items-center gap-2 mb-4">
            <Package className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-800">Low Stock Alerts</h3>
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