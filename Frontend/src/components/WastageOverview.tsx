import React, { useMemo, useState, useEffect } from 'react';
import { TrendingDown, Trash2, AlertCircle, Search, RotateCcw, Plus, Eye } from 'lucide-react';
import { Card } from './ui/card';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { AddWastageReasonModal } from './modal/AddWastageReasonModal';
import { ViewWastageReasonsModal, WastageReason } from './modal/ViewWastageReasonsModal';
import { multiplyNumeric } from '../utils/numericUtils';
import { wastageApi } from '../services/api';

type WastageItem = {
  id: string;
  name: string;
  category: string;
  reason: 'Expired' | 'Burnt' | 'Stale' | 'Damaged' | 'Spilled' | string;
  quantity: number;
  unit: string; // e.g., 'pcs', 'kg', 'L'
  unitCost: number; // per unit cost
  reportedBy: string;
  time: string; // e.g., '10:30 AM'
  date: string; // yyyy-mm-dd
};

export function WastageOverview() {
  const today = new Date().toISOString().slice(0,10);
  const [dateFrom, setDateFrom] = useState<string>(today);
  const [dateTo, setDateTo] = useState<string>(today);
  const [timePeriod, setTimePeriod] = useState<string>('Today');
  const [reason, setReason] = useState<string>('All Reasons');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const [addReasonOpen, setAddReasonOpen] = useState(false);
  const [viewReasonsOpen, setViewReasonsOpen] = useState(false);
  const [wastageReasons, setWastageReasons] = useState<WastageReason[]>([]);

  const [productWastage, setProductWastage] = useState<WastageItem[]>([]);
  const [ingredientWastage, setIngredientWastage] = useState<WastageItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Fetch wastage data from API
  useEffect(() => {
    const fetchWastageData = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);

        const response = await wastageApi.getAll();
        const wastageItems = response.items || [];

        // Separate product wastage (IDs like 'PW-001') from ingredient wastage (IDs like 'IW-001')
        const products: WastageItem[] = [];
        const ingredients: WastageItem[] = [];

        wastageItems.forEach((item: any) => {
          const wastageId = item.wastage_id || '';
          
          // Transform API response to WastageItem format
          const transformedItem: WastageItem = {
            id: wastageId,
            name: item.product_id?.name || item.ingredient_id?.name || 'Unknown',
            category: item.product_id?.category_id?.name || item.ingredient_id?.category_id?.name || 'Unknown',
            reason: item.reason_id?.description || 'Unknown',
            quantity: item.quantity || 0,
            unit: 'Unit', // Default unit, adjust if API provides units
            unitCost: item.unit_cost || 0,
            reportedBy: item.reported_by?.full_name || item.reported_by?.username || 'System',
            time: new Date(item.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            date: new Date(item.created_at).toISOString().slice(0, 10),
          };

          // Distinguish product vs ingredient wastage by ID prefix
          if (wastageId.startsWith('PW')) {
            products.push(transformedItem);
          } else if (wastageId.startsWith('IW')) {
            ingredients.push(transformedItem);
          }
        });

        setProductWastage(products);
        setIngredientWastage(ingredients);
      } catch (error) {
        console.error('Error fetching wastage data:', error);
        setFetchError('Failed to load wastage data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchWastageData();
  }, []);

  const filteredProduct = useMemo(() => {
    return productWastage.filter((i) => {
      if (i.date < dateFrom || i.date > dateTo) return false;
      if (reason !== 'All Reasons' && i.reason !== reason) return false;
      if (searchTerm.trim()) {
        const q = searchTerm.trim().toLowerCase();
        if (!i.name.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [productWastage, dateFrom, dateTo, reason, searchTerm]);

  const filteredIngredient = useMemo(() => {
    return ingredientWastage.filter((i) => {
      if (i.date < dateFrom || i.date > dateTo) return false;
      if (reason !== 'All Reasons' && i.reason !== reason) return false;
      if (searchTerm.trim()) {
        const q = searchTerm.trim().toLowerCase();
        if (!i.name.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [ingredientWastage, dateFrom, dateTo, reason, searchTerm]);

  // When timePeriod changes, update dateFrom/dateTo accordingly
  const applyTimePeriod = (period: string) => {
    const now = new Date();
    let start = new Date();
    let end = new Date();

    if (period === 'Today') {
      start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      end = start;
    } else if (period === 'All Time') {
      start = new Date(1970, 0, 1);
      end = now;
    } else if (period === 'This Week') {
      // start from Monday
      const day = now.getDay();
      const diff = now.getDate() - day + (day === 0 ? -6 : 1);
      start = new Date(now.setDate(diff));
      end = new Date();
    } else if (period === 'This Month') {
      start = new Date(now.getFullYear(), now.getMonth(), 1);
      end = new Date();
    } else if (period === 'This Year') {
      start = new Date(now.getFullYear(), 0, 1);
      end = new Date();
    }

    const toIso = (d: Date) => d.toISOString().slice(0,10);
    setDateFrom(toIso(start));
    setDateTo(toIso(end));
  };

  const resetFilters = () => {
    const todayIso = new Date().toISOString().slice(0,10);
    setDateFrom(todayIso);
    setDateTo(todayIso);
    setTimePeriod('Today');
    setReason('All Reasons');
    setSearchTerm('');
  };

  // KPIs
  const totalLoss = useMemo(() => {
    const sumProd = filteredProduct.reduce((s, it) => s + multiplyNumeric(it.unitCost, it.quantity), 0);
    const sumIng = filteredIngredient.reduce((s, it) => s + multiplyNumeric(it.unitCost, it.quantity), 0);
    return sumProd + sumIng;
  }, [filteredProduct, filteredIngredient]);

  const totalQty = useMemo(() => {
    const q1 = filteredProduct.reduce((s, it) => s + it.quantity, 0);
    const q2 = filteredIngredient.reduce((s, it) => s + it.quantity, 0);
    return q1 + q2;
  }, [filteredProduct, filteredIngredient]);

  const mostWasted = useMemo(() => {
    const all = [...filteredProduct, ...filteredIngredient];
    if (all.length === 0) return null;
    return all.reduce((max, it) => (it.quantity > (max?.quantity ?? -1) ? it : max), all[0]);
  }, [filteredProduct, filteredIngredient]);

  const reasonBadge = (r: string) => {
    if (r === 'Expired') return 'px-2 py-1 rounded bg-orange-100 text-orange-700 text-xs font-semibold';
    if (r === 'Burnt' || r === 'Damaged') return 'px-2 py-1 rounded bg-red-100 text-red-700 text-xs font-semibold';
    if (r === 'Stale') return 'px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs font-semibold';
    if (r === 'Spilled') return 'px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs font-semibold';
    return 'px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs font-semibold';
  };

  const formatDateDisplay = (dateStr: string, timeStr: string) => {
    const d = new Date(dateStr);
    const datePart = d.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    return `${datePart} • ${timeStr}`;
  };

  const exportToPDF = async () => {
    const pdf = new jsPDF();
    const tables = document.querySelectorAll('.wastage-table');
    
    for (let i = 0; i < tables.length; i++) {
      const canvas = await html2canvas(tables[i] as HTMLElement);
      const imgData = canvas.toDataURL('image/png');
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 295; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, -heightLeft, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      if (i < tables.length - 1) pdf.addPage();
    }

    pdf.save('wastage-report.pdf');
  };

  // Handler for saving a new reason
  const handleSaveWastageReason = (reason: WastageReason) => {
    setWastageReasons(prev => [...prev, reason]);
    setAddReasonOpen(false);
    // Optionally show a toast or notification here
  };

  // Handler for deleting a reason
  const handleDeleteWastageReason = (id: string) => {
    setWastageReasons(prev => prev.filter(r => r.id !== id));
    // Optionally show a toast or notification here
  };

  return (
    <Card className="p-6">
      {/* Toast/modal region */}
      <AddWastageReasonModal
        open={addReasonOpen}
        onClose={() => setAddReasonOpen(false)}
        onSave={handleSaveWastageReason}
      />
      <ViewWastageReasonsModal
        open={viewReasonsOpen}
        onClose={() => setViewReasonsOpen(false)}
        reasons={wastageReasons}
        onDelete={handleDeleteWastageReason}
      />

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="spinner mb-4 mx-auto w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
            <p className="text-gray-600">Loading wastage data...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {fetchError && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700">{fetchError}</p>
        </div>
      )}

      {/* Main Content */}
      {!isLoading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
              <div className="p-3 rounded bg-white text-red-500">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-red-800 font-semibold">Total Loss Today</div>
                <div className="text-lg font-bold text-red-600">Rs. {totalLoss.toLocaleString()}</div>
              </div>
            </div>

            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
              <div className="p-3 rounded bg-white text-orange-500">
                <Trash2 className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-orange-800 font-semibold">Total Wasted Qty</div>
                <div className="text-lg font-bold text-orange-700">{totalQty}</div>
              </div>
            </div>

            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
              <div className="p-3 rounded bg-white text-blue-500">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-blue-800 font-semibold">Most Wasted Item</div>
                <div className="text-lg font-bold text-blue-700">{mostWasted ? `${mostWasted.name} (${mostWasted.quantity} ${mostWasted.unit})` : '—'}</div>
              </div>
            </div>
          </div>

          {/* Global Filters */}
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
            <div className="flex flex-wrap gap-4 items-center">

              <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-orange-300 w-4 h-4" />
                  <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search by name..." className="pl-10 px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 w-64" />
                </div>

              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Date Range</label>
                <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setTimePeriod('Custom'); }} className="px-3 py-2 rounded-lg border border-orange-100 bg-orange-50 text-orange-900" />
                <span className="text-gray-400">to</span>
                <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setTimePeriod('Custom'); }} className="px-3 py-2 rounded-lg border border-orange-100 bg-orange-50 text-orange-900" />
              </div>

              <select value={timePeriod} onChange={(e) => { setTimePeriod(e.target.value); applyTimePeriod(e.target.value); }} className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900">
                <option>All Time</option>
                <option>Today</option>
                <option>This Week</option>
                <option>This Month</option>
                <option>This Year</option>
              </select>

              <select value={reason} onChange={(e) => setReason(e.target.value)} className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900">
                <option>All Reasons</option>
                <option>Expired</option>
                <option>Burnt</option>
                <option>Stale</option>
                <option>Damaged</option>
                <option>Spilled</option>
              </select>

              <button onClick={resetFilters} className="ml-2 text-red-500 hover:text-red-700 flex items-center gap-1 font-medium text-sm">
                  <RotateCcw className="w-4 h-4" /> Reset Filters
                </button>            

              <div className="relative ml-auto flex items-center gap-3">

                <button onClick={exportToPDF} className="ml-2 px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors">
                  Export PDF
                </button>

                <button
                  className="ml-2 px-4 py-2 rounded-lg bg-green-500 text-white font-bold shadow hover:bg-green-600 flex items-center gap-2 transition-colors"
                  onClick={() => setAddReasonOpen(true)}
                >
                  <Plus className="w-4 h-4" /> Add Wastage Reason
                </button>

                <button
                  className="ml-2 px-4 py-2 rounded-lg bg-green-500 text-white font-bold shadow hover:bg-green-600 flex items-center gap-2 transition-colors"
                  onClick={() => setViewReasonsOpen(true)}
                >
                  <Eye className="w-4 h-4" /> View Wastage Reasons
                </button>

                
              </div>
            </div>
          </div>

          {/* Dual Tables Grid */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* Product Wastage Table */}
            <div className="bg-white rounded-lg border border-orange-100 overflow-hidden wastage-table">
              <div className="rounded-t-lg bg-orange-100 p-4 flex items-center justify-between">
                  <h4 className="font-semibold text-orange-700">Product Wastage</h4>
                </div>
                <div className="p-4 overflow-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-orange-50 text-orange-700">
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Item Name</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Category</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Reason</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Quantity</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Loss Amount</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Reported By</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Date & Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProduct.map((r) => (
                      <tr key={r.id} className="border-b border-orange-100 hover:bg-[#FFF7F0] transition-colors">
                        <td className="py-3 px-4 font-medium text-gray-800">{r.name}</td>
                        <td className="py-3 px-4 text-gray-600">{r.category}</td>
                        <td className="py-3 px-4"> <span className={reasonBadge(r.reason)}>{r.reason}</span> </td>
                        <td className="py-3 px-4 text-gray-800">{r.quantity} {r.unit}</td>
                        <td className="py-3 px-4 text-red-700">Rs. {multiplyNumeric(r.unitCost, r.quantity).toLocaleString()}</td>
                        <td className="py-3 px-4 text-gray-600">{r.reportedBy}</td>
                        <td className="py-3 px-4 text-gray-600">{formatDateDisplay(r.date, r.time)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Ingredient Wastage Table */}
            <div className="bg-white rounded-lg border border-orange-100 overflow-hidden wastage-table">
              <div className="rounded-t-lg bg-orange-100 p-4 flex items-center justify-between">
                  <h4 className="font-semibold text-orange-700">Ingredient Wastage</h4>
                </div>
                <div className="p-4 overflow-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-orange-50 text-orange-700">
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Item Name</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Category</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Reason</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Quantity</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Loss Amount</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Reported By</th>
                      <th className="py-3 px-4 font-semibold border-b border-orange-200">Date & Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredIngredient.map((r) => (
                      <tr key={r.id} className="border-b border-orange-100 hover:bg-[#FFF7F0] transition-colors">
                        <td className="py-3 px-4 font-medium text-gray-800">{r.name}</td>
                        <td className="py-3 px-4 text-gray-600">{r.category}</td>
                        <td className="py-3 px-4"> <span className={reasonBadge(r.reason)}>{r.reason}</span> </td>
                        <td className="py-3 px-4 text-gray-800">{r.quantity} {r.unit}</td>
                        <td className="py-3 px-4 text-red-700">Rs. {multiplyNumeric(r.unitCost, r.quantity).toLocaleString()}</td>
                        <td className="py-3 px-4 text-gray-600">{r.reportedBy}</td>
                        <td className="py-3 px-4 text-gray-600">{formatDateDisplay(r.date, r.time)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </Card>
  );
}
