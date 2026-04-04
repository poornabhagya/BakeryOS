import React, { useState, useEffect } from 'react';
import { Package, Calendar, AlertTriangle, ArrowRight } from 'lucide-react';
import { batchApi, ingredientApi, ingredientWastagesApi } from '../../services/api';

type TimeFilter = 'Today' | 'This Week' | 'This Month';

type LowStockIngredient = {
  name: string;
  supplier: string;
  qty: string;
};

type ExpiringBatch = {
  id: string;
  item: string;
  daysLeft: number;
};

type IngredientWastageRow = {
  id: string;
  ingredientName: string;
  quantity: number;
  reason: string;
};

export function StorekeeperDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('Today');

  const [lowStockIngredients, setLowStockIngredients] = useState<LowStockIngredient[]>([]);
  const [expiringBatches, setExpiringBatches] = useState<ExpiringBatch[]>([]);
  const [ingredientWastage, setIngredientWastage] = useState<IngredientWastageRow[]>([]);

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

  const fetchAllIngredientWastagePages = async () => {
    let page = 1;
    let hasNext = true;
    const allItems: any[] = [];

    while (hasNext) {
      const response = await ingredientWastagesApi.getAll(page);
      const pageItems = response?.items || [];
      allItems.push(...pageItems);
      hasNext = Boolean(response?.nextPage);
      page += 1;
    }

    return allItems;
  };

  useEffect(() => {
    const fetchStorekeeperData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Real-time fetches (no time filtering): low stock ingredients + ingredient batches
        const [lowStockData, batchesData, ingredientWastageItems] = await Promise.all([
          ingredientApi.getLowStock(),
          batchApi.getIngredientBatches(),
          fetchAllIngredientWastagePages(),
        ]);

        const lowStockSource = Array.isArray(lowStockData?.results)
          ? lowStockData.results
          : Array.isArray(lowStockData)
          ? lowStockData
          : [];

        // Low stock ingredients must show real ingredient name/supplier/qty.
        const lowStockItems = lowStockSource
          .filter((item: any) => Number(item.total_quantity || 0) <= Number(item.low_stock_threshold || 0))
          .slice(0, 10)
          .map((item: any) => ({
            name: item.name || 'Unknown',
            qty: `${Number(item.total_quantity || 0)} ${item.base_unit || 'units'}`,
            supplier: item.supplier || 'Not specified',
          }));
        setLowStockIngredients(lowStockItems);

        const batchSource = Array.isArray(batchesData)
          ? batchesData
          : Array.isArray((batchesData as any)?.results)
          ? (batchesData as any).results
          : [];

        // Expiring ingredient batches within 7 days (real-time, no time filter).
        const today = new Date();
        const sevenDaysLater = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        
        const expirying = batchSource
          .filter((batch: any) => {
            const expiryDateRaw = batch.expire_date || batch.expiry_date;
            const expiryDate = expiryDateRaw ? new Date(expiryDateRaw) : null;
            if (!expiryDate || Number.isNaN(expiryDate.getTime())) return false;
            return expiryDate >= today && expiryDate <= sevenDaysLater;
          })
          .sort((a: any, b: any) => new Date(a.expire_date || a.expiry_date).getTime() - new Date(b.expire_date || b.expiry_date).getTime())
          .slice(0, 8)
          .map((batch: any) => {
            const expiryDate = new Date(batch.expire_date || batch.expiry_date);
            const daysLeft = Math.ceil((expiryDate.getTime() - today.getTime()) / (24 * 60 * 60 * 1000));
            return {
              id: batch.batch_id || `BATCH-${batch.id || 'NA'}`,
              item: batch.ingredient_name || 'Unknown',
              daysLeft: Math.max(0, daysLeft),
            };
          });
        setExpiringBatches(expirying);

        // Time-filtered ingredient wastage report.
        const { start, end } = getFilterRange(timeFilter);
        const mappedWastage = (ingredientWastageItems || [])
          .filter((item: any) => {
            const createdAt = new Date(item.created_at);
            return !Number.isNaN(createdAt.getTime()) && createdAt >= start && createdAt <= end;
          })
          .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 10)
          .map((item: any) => ({
            id: item.wastage_id || String(item.id || Math.random()),
            ingredientName: item.ingredient_name || 'Unknown',
            quantity: Number(item.quantity || 0),
            reason: item.reason_text || 'Unknown',
          }));

        setIngredientWastage(mappedWastage);
      } catch (err) {
        console.error('Error fetching storekeeper dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStorekeeperData();
  }, [timeFilter]);
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
      
      {/* FILTER */}
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

      {/* ROW 3: INGREDIENT WASTAGE REPORT (FILTERED) */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-800">Ingredient Wastage Report ({timeFilter})</h3>
        </div>
        <div className="overflow-hidden">
          {ingredientWastage.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No ingredient wastage reported for {timeFilter.toLowerCase()}</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Ingredient Name</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Quantity Wasted</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Reason</th>
                </tr>
              </thead>
              <tbody>
                {ingredientWastage.map((row) => (
                  <tr key={row.id} className="border-b border-gray-100 last:border-b-0">
                    <td className="py-2 px-2 text-gray-800 font-medium">{row.ingredientName}</td>
                    <td className="py-2 px-2 text-red-600 font-bold">{row.quantity}</td>
                    <td className="py-2 px-2 text-gray-600">{row.reason}</td>
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