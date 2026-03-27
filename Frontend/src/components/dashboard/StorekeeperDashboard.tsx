import React, { useState, useEffect } from 'react';
import { Package, Calendar, AlertTriangle, ArrowRight } from 'lucide-react';
import { inventoryApi, batchApi } from '../../services/api';

export function StorekeeperDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [lowStockIngredients, setLowStockIngredients] = useState<any[]>([]);
  const [expiringBatches, setExpiringBatches] = useState<any[]>([]);

  useEffect(() => {
    const fetchStorekeeperData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch low stock items
        const [lowStockData, batchesData] = await Promise.all([
          inventoryApi.getLowStock(),
          batchApi?.list?.().catch(() => []) || Promise.resolve([]),
        ]);

        // Process low stock items with supplier info
        const lowStockItems = Array.isArray(lowStockData) 
          ? lowStockData.slice(0, 6).map((item: any) => ({
              name: item.name || item.product_name || 'Unknown',
              qty: `${item.current_stock || 0} ${item.unit || 'units'}`,
              supplier: item.supplier_name || item.supplier || 'Not specified',
            }))
          : [];
        setLowStockIngredients(lowStockItems);

        // Process expiring batches (filter by expiry date within 7 days)
        const today = new Date();
        const sevenDaysLater = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        
        const expirying = Array.isArray(batchesData) 
          ? batchesData
              .filter((batch: any) => {
                const expiryDate = new Date(batch.expiry_date || batch.batch_expiration_date);
                return expiryDate <= sevenDaysLater && expiryDate > today;
              })
              .slice(0, 5)
              .map((batch: any) => {
                const expiryDate = new Date(batch.expiry_date || batch.batch_expiration_date);
                const daysLeft = Math.ceil((expiryDate.getTime() - today.getTime()) / (24 * 60 * 60 * 1000));
                return {
                  id: batch.id || batch.batch_number || '#BAT-' + Math.random().toString(36).substr(2, 9),
                  item: batch.product_name || batch.name || 'Unknown',
                  expiry: expiryDate.toISOString().split('T')[0],
                  daysLeft: Math.max(0, daysLeft),
                };
              })
          : [];
        setExpiringBatches(expirying);
      } catch (err) {
        console.error('Error fetching storekeeper dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStorekeeperData();
  }, []);
  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <p className="font-semibold">Error loading dashboard</p>
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      {/* ROW 1: METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <Package className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Low Stock Items</div>
            <div className="text-lg font-bold text-red-700">{lowStockIngredients.length} Items</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-yellow-50 border border-yellow-200">
          <div className="p-3 rounded bg-white text-yellow-600">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-yellow-800 font-semibold">Expiring Soon</div>
            <div className="text-lg font-bold text-yellow-700">{expiringBatches.length} Batches</div>
          </div>
        </div>
      </div>

      {/* ROW 2: DATA TABLES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* LEFT: Low Stock List */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-semibold text-gray-800">Low Stock Ingredients</h3>
            </div>
            <button className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
              View All <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-hidden">
            {lowStockIngredients.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No low stock items</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Item</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Supplier</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Qty</th>
                  </tr>
                </thead>
                <tbody>
                  {lowStockIngredients.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                      <td className="py-2 px-2 text-gray-600">{item.supplier}</td>
                      <td className="py-2 px-2 text-red-600 font-bold">{item.qty}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* RIGHT: Expiring Batches */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">Expiring Batches (7 Days)</h3>
          </div>
          <div className="overflow-hidden">
            {expiringBatches.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No batches expiring soon</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Batch ID</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Item</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Expires In</th>
                  </tr>
                </thead>
                <tbody>
                  {expiringBatches.map((batch, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-600">{batch.id}</td>
                      <td className="py-2 px-2 text-gray-800 font-medium">{batch.item}</td>
                      <td className="py-2 px-2">
                        <span className="bg-red-100 text-red-700 px-2 py-1 rounded-full text-xs font-bold">
                          {batch.daysLeft} days
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}