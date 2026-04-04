import React, { useState, useEffect, useMemo } from 'react';
import { Flame, ChefHat, Star } from 'lucide-react';
import { inventoryApi, wastageApi, analyticsApi } from '../../services/api';

type TimeFilter = 'Today' | 'This Week' | 'This Month';

type LowStockProduct = {
  name: string;
  remaining: number;
  priority: 'Urgent' | 'High' | 'Medium';
};

type WastageRow = {
  id: string;
  item: string;
  qty: number;
  reason: string;
  createdAt: string;
};

type TopSellingRow = {
  product_name: string;
  quantity_sold: number;
};

export function BakerDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('Today');

  const [lowStockProducts, setLowStockProducts] = useState<LowStockProduct[]>([]);
  const [filteredWastage, setFilteredWastage] = useState<WastageRow[]>([]);
  const [topSellingProducts, setTopSellingProducts] = useState<TopSellingRow[]>([]);

  const getFilterRange = (filter: TimeFilter) => {
    const now = new Date();
    const end = new Date(now);
    end.setHours(23, 59, 59, 999);

    const start = new Date(now);
    if (filter === 'Today') {
      start.setHours(0, 0, 0, 0);
    } else if (filter === 'This Week') {
      const day = start.getDay();
      const diff = day === 0 ? -6 : 1 - day;
      start.setDate(start.getDate() + diff);
      start.setHours(0, 0, 0, 0);
    } else {
      start.setDate(1);
      start.setHours(0, 0, 0, 0);
    }

    return { start, end };
  };

  const toIsoDate = (value: Date) => value.toISOString().slice(0, 10);

  const fetchAllWastagePages = async () => {
    let page = 1;
    let hasNext = true;
    const allItems: any[] = [];

    while (hasNext) {
      const response = await wastageApi.getAll(page);
      const pageItems = response?.items || [];
      allItems.push(...pageItems);
      hasNext = Boolean(response?.nextPage);
      page += 1;
    }

    return allItems;
  };

  useEffect(() => {
    const fetchBakerData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const { start, end } = getFilterRange(timeFilter);
        const dateFrom = toIsoDate(start);
        const dateTo = toIsoDate(end);

        const [lowStockData, allWastageItems, productStats] = await Promise.all([
          inventoryApi.getLowStock(),
          fetchAllWastagePages(),
          analyticsApi.getProductStats(dateFrom, dateTo),
        ]);

        // Products: always real-time and unfiltered.
        const lowProducts = Array.isArray(lowStockData) 
          ? lowStockData.slice(0, 8).map((item: any) => ({
              name: item.name || 'Unknown',
              remaining: Number(item.current_stock || 0),
              priority: Number(item.current_stock || 0) === 0
                ? 'Urgent'
                : Number(item.current_stock || 0) <= 5
                ? 'High'
                : 'Medium',
            }))
          : [];
        setLowStockProducts(lowProducts);

        // Wastage: apply selected time filter.
        const wastageRows = (allWastageItems || [])
          .filter((item: any) => {
            const createdAt = new Date(item.created_at);
            return !Number.isNaN(createdAt.getTime()) && createdAt >= start && createdAt <= end;
          })
          .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 8)
          .map((item: any) => ({
            id: item.wastage_id || String(item.id || Math.random()),
            item: item.product_name || item.ingredient_name || 'Unknown',
            qty: Number(item.quantity || 0),
            reason: item.reason_text || 'Unknown',
            createdAt: item.created_at,
          }));

        setFilteredWastage(wastageRows);

        const topRows = Array.isArray(productStats?.top_products)
          ? productStats.top_products.slice(0, 6).map((item: any) => ({
              product_name: item.product_name || 'Unknown',
              quantity_sold: Number(item.quantity_sold || 0),
            }))
          : [];
        setTopSellingProducts(topRows);
      } catch (err) {
        console.error('Error fetching baker dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBakerData();
  }, [timeFilter]);

  const criticalBakeCount = useMemo(
    () => lowStockProducts.filter((p) => p.priority === 'Urgent' || p.priority === 'High').length,
    [lowStockProducts]
  );

  const wastageCount = filteredWastage.length;
  const topProduct = topSellingProducts[0] || null;
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
      
      <div className="bg-white rounded-lg shadow-sm p-4 flex items-center gap-4">
        <label className="text-sm font-semibold text-gray-700">Filter by:</label>
        <select
          value={timeFilter}
          onChange={(e) => setTimeFilter(e.target.value as TimeFilter)}
          className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-gray-800 font-medium hover:bg-orange-100 transition-colors cursor-pointer"
        >
          <option value="Today">Today</option>
          <option value="This Week">This Week</option>
          <option value="This Month">This Month</option>
        </select>
      </div>

      {/* HEADER: Production Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Production Alert */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <ChefHat className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Items to Bake</div>
            <div className="text-lg font-bold text-orange-700">{criticalBakeCount} Items Critical</div>
          </div>
        </div>

        {/* Wastage Count */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Wastage Issues Reported</div>
            <div className="text-lg font-bold text-red-700">{wastageCount} Issues Reported</div>
          </div>
        </div>

        {/* Top #1 Sold Product */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
          <div className="p-3 rounded bg-white text-blue-600">
            <Star className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-blue-800 font-semibold">Top #1 Sold Product</div>
            {topProduct ? (
              <>
                <div className="text-lg font-bold text-blue-700">{topProduct.product_name}</div>
                <div className="text-sm font-semibold text-blue-600">{topProduct.quantity_sold} pcs sold</div>
              </>
            ) : (
              <div className="text-lg font-bold text-blue-700">No Sales Yet</div>
            )}
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

        {/* RIGHT: TOP SELLING PRODUCTS */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-5 h-5 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-800">Top Selling Products</h3>
          </div>
          <div className="overflow-hidden">
            {topSellingProducts.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No sales recorded for {timeFilter.toLowerCase()}</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Item Name</th>
                    <th className="text-left py-2 px-2 font-semibold text-gray-700">Quantity Sold</th>
                  </tr>
                </thead>
                <tbody>
                  {topSellingProducts.map((item, index) => (
                    <tr key={`${item.product_name}-${index}`} className="border-b border-gray-100 last:border-b-0">
                      <td className="py-2 px-2 text-gray-800 font-medium">{item.product_name}</td>
                      <td className="py-2 px-2 text-blue-700 font-semibold">{item.quantity_sold} pcs</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

      </div>

      {/* FILTERED WASTAGE */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Flame className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-800">{timeFilter} Wastage Report</h3>
        </div>
        <div className="overflow-hidden">
          {filteredWastage.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No wastage reported for {timeFilter.toLowerCase()}</p>
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
                {filteredWastage.map((item) => (
                  <tr key={item.id} className="border-b border-gray-100 last:border-b-0">
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