import React, { useMemo, useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Tag, Zap, Edit, Trash2, Plus, Search, ToggleLeft, Loader } from 'lucide-react';
import { AddDiscountModal } from './modal/AddDiscountModal';
import { EditDiscountModal } from './modal/EditDiscountModal';
import { useAuth } from '../context/AuthContext'; // 1. Auth Import
import apiClient from '../services/api';

type Discount = {
  id: string;
  name: string;
  kind: 'percent' | 'fixed';
  value: string; 
  applicableTo: string;
  validity: string;
  active: boolean;
};

const mockDiscounts: Discount[] = [
  { id: '#D001', name: 'Evening Happy Hour', kind: 'percent', value: '50%', applicableTo: 'All Buns', validity: 'Daily 8 PM - 9 PM', active: true },
  { id: '#D002', name: 'Staff Lunch', kind: 'fixed', value: 'Rs. 150', applicableTo: 'Rice & Curry', validity: 'Weekdays', active: false },
  { id: '#D003', name: 'Christmas Special', kind: 'percent', value: '10%', applicableTo: 'Cakes', validity: 'Dec 20 - Dec 25', active: true },
];

export default function DiscountManagement() {
  const { user } = useAuth(); // 2. Get User
  // 3. Define Permission: Only Manager has full access
  const isManager = user?.role === 'Manager';

  // --- State: API Data ---
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // --- Fetch Discounts from API ---
  useEffect(() => {
    const fetchDiscounts = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);
        const response = await apiClient.discounts.getAll();
        // response.items already contains UI-formatted discounts
        const uiDiscounts = response.items.map((apiDiscount: any) => ({
          id: apiDiscount.id,
          name: apiDiscount.name,
          kind: apiDiscount.kind,
          value: apiDiscount.value,
          applicableTo: apiDiscount.applicable_to || 'All Items',
          validity: apiDiscount.validity || 'Always',
          active: apiDiscount.status === 'active',
        }));
        setDiscounts(uiDiscounts);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch discounts';
        setFetchError(errorMsg);
        console.error('Error fetching discounts:', error);
        // Fall back to mock data
        setDiscounts(mockDiscounts);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDiscounts();
  }, []);

  // --- Additional State ---
  const [addDiscountOpen, setAddDiscountOpen] = useState(false);
  const [editDiscountOpen, setEditDiscountOpen] = useState(false);
  const [editingDiscount, setEditingDiscount] = useState<any | null>(null);
  
  // Mock categories and items
  const categories = ['Buns', 'Cakes', 'Drinks'];
  const items = [
    { id: 'B001', name: 'Fish Bun' },
    { id: 'B002', name: 'Tea Bun' },
    { id: 'C001', name: 'Butter Cake' },
    { id: 'D001', name: 'Orange Juice' },
  ];
  
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'All'|'Active'|'Inactive'>('All');
  const [validFrom, setValidFrom] = useState<string>('');
  const [validTo, setValidTo] = useState<string>('');
  const [selected, setSelected] = useState<Record<string,boolean>>({});

  const filtered = useMemo(() => {
    return discounts.filter(d => {
      if (search.trim() && !d.name.toLowerCase().includes(search.trim().toLowerCase())) return false;
      if (statusFilter === 'Active' && !d.active) return false;
      if (statusFilter === 'Inactive' && d.active) return false;
      return true;
    });
  }, [discounts, search, statusFilter, validFrom, validTo]);

  const toggleActive = (id: string) => {
    // Extra security: Only Manager can toggle
    if (!isManager) return;
    setDiscounts(prev => prev.map(d => d.id === id ? { ...d, active: !d.active } : d));
  };

  const deleteSelected = () => {
    const sel = Object.keys(selected).filter(k => selected[k]);
    if (sel.length === 0) return;
    setDiscounts(prev => prev.filter(d => !sel.includes(d.id)));
    setSelected({});
  };

  const toggleSelect = (id: string) => {
    setSelected(s => ({ ...s, [id]: !s[id] }));
  };

  const activeCount = discounts.filter(d => d.active).length;
  const totalDiscountToday = 1200; 

  return (
    <div className="p-6">
      <AddDiscountModal
        open={addDiscountOpen}
        onClose={() => setAddDiscountOpen(false)}
        onSave={discount => {
          setDiscounts(prev => [
            ...prev,
            {
              id: discount.id,
              name: discount.name,
              kind: discount.type === 'percentage' ? 'percent' : 'fixed',
              value: discount.type === 'percentage' ? `${discount.value}%` : `Rs. ${discount.value}`,
              applicableTo:
                discount.applicableTo === 'all'
                  ? 'All Items'
                  : discount.applicableTo === 'category'
                  ? discount.category
                  : items.find(i => i.id === discount.item)?.name || '',
              validity: [discount.startDate, discount.endDate].filter(Boolean).join(' to ') || '—',
              active: true,
            },
          ]);
        }}
        categories={categories}
        items={items}
      />
      <EditDiscountModal
        open={editDiscountOpen}
        onClose={() => {
          setEditDiscountOpen(false);
          setEditingDiscount(null);
        }}
        discount={editingDiscount}
        onUpdate={async (updated) => {
          try {
            // Map UI types to API types
            const discountType = updated.type === 'percentage' ? 'Percentage' : 'FixedAmount';
            const applicableTo = updated.applicableTo === 'all' ? 'All' : updated.applicableTo === 'category' ? 'Category' : 'Product';
            
            // Prepare data for API
            const updateData: any = {
              name: updated.name,
              discount_type: discountType,
              value: updated.value,
              applicable_to: applicableTo,
              start_date: updated.startDate || null,
              end_date: updated.endDate || null,
              start_time: updated.startTime || null,
              end_time: updated.endTime || null,
            };
            
            // Add target IDs only if applicable_to requires them
            if (applicableTo === 'Category' && updated.targetId) {
              updateData.target_category_id = updated.targetId;
              updateData.target_product_id = null;
            } else if (applicableTo === 'Product' && updated.targetId) {
              updateData.target_product_id = updated.targetId;
              updateData.target_category_id = null;
            } else {
              updateData.target_category_id = null;
              updateData.target_product_id = null;
            }
            
            // Make API call to update database
            await apiClient.discounts.update(updated.id as number, updateData);
            
            // Update local state only after successful API call
            setDiscounts(prev => prev.map(d =>
              d.id === updated.id
                ? {
                    ...d,
                    name: updated.name,
                    kind: updated.type === 'percentage' ? 'percent' : 'fixed',
                    value: updated.type === 'percentage' ? `${updated.value}%` : `Rs. ${updated.value}`,
                    applicableTo:
                      updated.applicableTo === 'all'
                        ? 'All Items'
                        : updated.applicableTo === 'category'
                        ? updated.targetId || ''
                        : items.find(i => i.id === updated.targetId)?.name || '',
                    validity: [updated.startDate, updated.endDate].filter(Boolean).join(' to ') || '—',
                  }
                : d
            ));
            setEditDiscountOpen(false);
            setEditingDiscount(null);
          } catch (error) {
            console.error('Error updating discount:', error);
            alert('Failed to update discount. Please try again.');
          }
        }}
        categories={categories}
        items={items}
      />
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-purple-50 border border-purple-200">
          <div className="p-3 rounded bg-white text-purple-600">
            <Tag className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-purple-800 font-semibold">Total Discount Given (Today)</div>
            <div className="text-lg font-bold text-purple-700">Rs. {totalDiscountToday.toLocaleString()}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
          <div className="p-3 rounded bg-white text-blue-600">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-blue-800 font-semibold">Active Promotions</div>
            <div className="text-lg font-bold text-blue-700">{activeCount} Active</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6 flex flex-wrap gap-4 items-center">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-orange-300 w-4 h-4" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search offers (e.g., Christmas)..." className="pl-10 px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 w-64 focus:outline-none focus:ring-2 focus:ring-orange-400 placeholder-orange-300" />
        </div>

        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as any)} className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer">
          <option>All</option>
          <option>Active</option>
          <option>Inactive</option>
        </select>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Validity Period</label>
          <input type="date" value={validFrom} onChange={(e) => setValidFrom(e.target.value)} className="px-3 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <span className="text-gray-400">to</span>
          <input type="date" value={validTo} onChange={(e) => setValidTo(e.target.value)} className="px-3 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400" />
        </div>
      </div>

      {/* Table */}
      <div className="border border-orange-100 rounded-lg overflow-hidden bg-white">
        <div className="rounded-t-lg bg-orange-50 p-4 flex items-center justify-between">
          <h4 className="font-semibold text-orange-700">Discounts & Promotions</h4>
        </div>
        <div className="p-4 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-orange-50 text-orange-700">
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Name</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Type & Value</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Applicable To</th>
                <th className="py-3 px-4 font-semibold border-b border-orange-200">Validity</th>
                {/* 4. Hide Status & Actions Headers for Cashier */}
                {isManager && <th className="py-3 px-4 font-semibold border-b border-orange-200">Status</th>}
                {isManager && <th className="py-3 px-4 font-semibold border-b border-orange-200">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => {
                // ... (Parsing logic remains same) ...
                let type: 'percentage' | 'fixed' = d.kind === 'percent' ? 'percentage' : 'fixed';
                let valueNum = type === 'percentage' ? Number((d.value || '').replace('%', '')) : Number((d.value || '').replace('Rs.', '').replace(/[^\d.]/g, ''));
                let applicableTo: 'all' | 'category' | 'item' = 'all';
                let targetId: string | undefined = undefined;
                if (d.applicableTo === 'All Items') applicableTo = 'all';
                else if (categories.includes(d.applicableTo)) {
                  applicableTo = 'category';
                  targetId = d.applicableTo;
                } else if (items.some(i => i.name === d.applicableTo)) {
                  applicableTo = 'item';
                  targetId = items.find(i => i.name === d.applicableTo)?.id;
                }
                let startDate = undefined, endDate = undefined;
                if (d.validity && d.validity.includes(' to ')) {
                  [startDate, endDate] = d.validity.split(' to ');
                }

                return (
                  <tr key={d.id} className="border-b border-orange-100 hover:bg-[#FFF7F0] transition-colors">
                    <td className="py-3 px-4 text-gray-800 flex items-center gap-3">
                      {/* Checkbox only for Manager */}
                      {isManager && (
                        <input type="checkbox" checked={!!selected[d.id]} onChange={() => toggleSelect(d.id)} className="w-4 h-4" />
                      )}
                      <span className="font-medium">{d.name}</span>
                    </td>
                    <td className="py-3 px-4">
                      {d.kind === 'percent' ? (
                        <span className="px-2 py-1 rounded bg-orange-100 text-orange-700 text-xs font-semibold">{d.value}</span>
                      ) : (
                        <span className="px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs font-semibold">{d.value}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-600">{d.applicableTo}</td>
                    <td className="py-3 px-4 text-gray-600">{d.validity}</td>
                    
                    {/* 5. Hide Status Toggle for Cashier */}
                    {isManager && (
                      <td className="py-3 px-4">
                        <button onClick={() => toggleActive(d.id)} className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${d.active ? 'bg-green-500' : 'bg-gray-300'}`}> 
                          <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${d.active ? 'translate-x-6' : 'translate-x-1'}`} />
                        </button>
                      </td>
                    )}

                    {/* 6. Hide Actions Column for Cashier */}
                    {isManager && (
                      <td className="py-3 px-4 flex gap-2">
                        <button
                          title="Edit"
                          className="p-2 rounded hover:bg-orange-100 text-orange-500"
                          onClick={() => {
                            setEditingDiscount({
                              id: d.id,
                              name: d.name,
                              type,
                              value: valueNum,
                              applicableTo,
                              targetId,
                              startDate,
                              endDate,
                            });
                            setEditDiscountOpen(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button title="Delete" onClick={() => setDiscounts(prev => prev.filter(x => x.id !== d.id))} className="p-2 rounded hover:bg-orange-100 text-red-500">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 7. Hide "Add Discount" Button for Cashier */}
      {isManager && (
        <div className="flex justify-end mt-6">
          <button
            className="px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors"
            onClick={() => setAddDiscountOpen(true)}
          >
            <Plus className="w-5 h-5" />
            Add Discount
          </button>
        </div>
      )}
    </div>
  );
}