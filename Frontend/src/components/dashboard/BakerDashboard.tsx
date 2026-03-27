import React, { useState, useEffect } from 'react';
import { Flame, ChefHat, AlertCircle, Package } from 'lucide-react';
import { inventoryApi, wastageApi, analyticsApi } from '../../services/api';

export function BakerDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [lowStockProducts, setLowStockProducts] = useState<any[]>([]);
  const [lowIngredients, setLowIngredients] = useState<any[]>([]);
  const [todaysWastage, setTodaysWastage] = useState<any[]>([]);
  const [wastageCount, setWastageCount] = useState(0);

  useEffect(() => {
    const fetchBakerData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch low stock products and ingredients
        const [lowStockData, wastageData] = await Promise.all([
          inventoryApi.getLowStock(),
          wastageApi.getAll(1),
        ]);

        // Process low stock items (products for baking)
        const lowProducts = Array.isArray(lowStockData) 
          ? lowStockData.slice(0, 5).map((item: any) => ({
              name: item.name || 'Unknown',
              remaining: item.current_stock || 0,
              target: item.reorder_level || 50,
              priority: (item.current_stock || 0) === 0 ? 'Urgent' : (item.current_stock || 0) <= 5 ? 'High' : 'Medium',
            }))
          : [];
        setLowStockProducts(lowProducts);

        // Process wastage (today's wastage)
        const todayWastages = wastageData?.items 
          ? wastageData.items.slice(0, 3).map((item: any) => ({
              item: item.name || 'Unknown',
              qty: item.quantity || 0,
              reason: item.reason || 'Unknown',
            }))
          : [];
        setTodaysWastage(todayWastages);
        setWastageCount(todayWastages.length);

        // No low ingredients endpoint available yet - show empty state
        setLowIngredients([]);
      } catch (err) {
        console.error('Error fetching baker dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBakerData();
  }, []);
  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
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
      
      {/* HEADER: Production Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Production Alert */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <ChefHat className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Items to Bake</div>
            <div className="text-lg font-bold text-orange-700">{lowStockProducts.filter(p => p.priority === 'Urgent' || p.priority === 'High').length} Items Critical</div>
          </div>
        </div>

        {/* Wastage Count */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Today's Wastage</div>
            <div className="text-lg font-bold text-red-700">{wastageCount} Issues Reported</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* LEFT: BAKE NOW LIST */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Flame className="w-5 h-5 text-orange-500" />
            <h3 className="text-lg font-semibold text-gray-800">Bake Now! (Low Stock)</h3>
          </div>
          <div className="overflow-hidden">
            {lowStockProducts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No low stock items</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Item</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Remaining</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {lowStockProducts.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                      <td className="py-2 px-2 text-red-600 font-bold">{item.remaining} pcs</td>
                      <td className="py-2 px-2">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${item.priority === 'Urgent' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                          {item.priority}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* RIGHT: LOW INGREDIENTS */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-800">Low Ingredient Alert</h3>
          </div>
          <div className="overflow-hidden">
            {lowIngredients.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No low ingredients</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Ingredient</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Qty</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {lowIngredients.map((item, index) => (
                    <tr key={index} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                      <td className="py-2 px-2 text-gray-600">{item.qty}</td>
                      <td className="py-2 px-2 text-red-600 font-semibold">{item.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

      </div>

      {/* TODAY'S WASTAGE */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Flame className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-800">Today's Wastage Report</h3>
        </div>
        <div className="overflow-hidden">
          {todaysWastage.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No wastage reported today</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Item</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Quantity Wasted</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Reason</th>
                </tr>
              </thead>
              <tbody>
                {todaysWastage.map((item, index) => (
                  <tr key={index} className="border-b border-gray-100 last:border-b-0">
                    <td className="py-2 px-2 text-gray-800 font-medium">{item.item}</td>
                    <td className="py-2 px-2 text-red-600 font-bold">{item.qty}</td>
                    <td className="py-2 px-2 text-gray-600">{item.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}