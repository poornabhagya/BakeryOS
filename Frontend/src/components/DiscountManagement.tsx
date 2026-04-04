import React, { useMemo, useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Tag, Zap, Edit, Trash2, Plus, Search, ToggleLeft, Loader } from 'lucide-react';
import { AddDiscountModal } from './modal/AddDiscountModal';
import { EditDiscountModal } from './modal/EditDiscountModal';
import { DeleteConfirmationModal } from './modal/DeleteConfirmationModal';
import { useAuth } from '../context/AuthContext'; // 1. Auth Import
import apiClient from '../services/api';

type Discount = {
  id: string | number;
  name: string;
  kind: 'percent' | 'fixed';
  value: string; 
  applicableTo: string;
  validity: string;
  startDate: string | null;  // Raw date from API (YYYY-MM-DD format)
  endDate: string | null;    // Raw date from API (YYYY-MM-DD format)
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
  const canViewDiscounts = user?.role === 'Manager' || user?.role === 'Cashier';

  if (!canViewDiscounts) {
    return (
      <div className="p-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 font-semibold">
          Access Denied: You do not have permission to view Discount Management.
        </div>
      </div>
    );
  }

  // --- State: API Data ---
  const [discounts, setDiscounts] = useState<Discount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // --- Helper: Format dates for display ---
  const formatValidityPeriod = (startDate: string | null, endDate: string | null): string => {
    if (!startDate && !endDate) return 'Always';
    
    const formatDate = (dateStr: string | null): string => {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return '';
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      } catch {
        return '';
      }
    };
    
    const formattedStart = formatDate(startDate);
    const formattedEnd = formatDate(endDate);
    
    if (formattedStart && formattedEnd) return `${formattedStart} to ${formattedEnd}`;
    if (formattedStart) return `From ${formattedStart}`;
    if (formattedEnd) return `Until ${formattedEnd}`;
    return 'Always';
  };

  // --- Fetch Discounts from API ---
  useEffect(() => {
    const fetchDiscounts = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);
        const response = await apiClient.discounts.getAll();
        // Map from API response to UI format
        const uiDiscounts = response.items.map((apiDiscount: any) => {
          // Extract dates from API response (snake_case keys from Django serializer)
          const startDate = apiDiscount.start_date || null;
          const endDate = apiDiscount.end_date || null;
          
          // Format validity display string using helper
          const validity = formatValidityPeriod(startDate, endDate);
          
          return {
            id: apiDiscount.id,
            name: apiDiscount.name,
            kind: apiDiscount.discount_type === 'Percentage' ? 'percent' : 'fixed',
            value: apiDiscount.discount_type === 'Percentage' ? `${apiDiscount.value}%` : `Rs. ${apiDiscount.value}`,
            applicableTo: apiDiscount.applicable_to === 'All' ? 'All Items' : (apiDiscount.applicable_to || 'All Items'),
            validity: validity,
            startDate: startDate,
            endDate: endDate,
            active: apiDiscount.is_active === true,
          };
        });
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
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [discountToDelete, setDiscountToDelete] = useState<any | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [totalDiscountToday, setTotalDiscountToday] = useState(0);
  
  // Fetch today's total discount from analytics endpoint
  useEffect(() => {
    const fetchTodayDiscountTotal = async () => {
      try {
        // Get today's date range
        const today = new Date();
        const dateStr = today.toISOString().split('T')[0]; // YYYY-MM-DD format
        
        console.log(`[DiscountManagement] Fetching discount total for ${dateStr}`);
        
        // Call analytics API with today's date range
        const response = await apiClient.analytics.getSalesStats(dateStr, dateStr);
        
        if (response && response.total_discount !== undefined) {
          setTotalDiscountToday(response.total_discount);
          console.log(`[DiscountManagement] Today's discount total: Rs. ${response.total_discount}`);
        }
      } catch (error) {
        console.error('[DiscountManagement] Error fetching discount total:', error);
        // Keep default value of 0 on error
      }
    };

    fetchTodayDiscountTotal();
  }, []);
  
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
      // Search filter
      if (search.trim() && !d.name.toLowerCase().includes(search.trim().toLowerCase())) return false;
      
      // Status filter
      if (statusFilter === 'Active' && !d.active) return false;
      if (statusFilter === 'Inactive' && d.active) return false;
      
      // Date range filter for Validity Period
      if (validFrom || validTo) {
        // If discount has no start/end dates, it's "Always" valid -> show in all filters
        if (!d.startDate && !d.endDate) {
          return true;
        }
        
        // Parse filter dates
        const filterStart = validFrom ? new Date(validFrom) : null;
        const filterEnd = validTo ? new Date(validTo) : null;
        
        // If no filter dates selected, include discount
        if (!filterStart && !filterEnd) return true;
        
        // Parse discount dates
        const discountStart = d.startDate ? new Date(d.startDate) : null;
        const discountEnd = d.endDate ? new Date(d.endDate) : null;
        
        // Check if discount period overlaps with filter period
        // Discount overlaps with filter if:
        // (discountStart <= filterEnd) AND (discountEnd >= filterStart)
        
        if (filterStart && discountEnd && discountEnd < filterStart) {
          // Discount ends before filter starts -> exclude
          return false;
        }
        
        if (filterEnd && discountStart && discountStart > filterEnd) {
          // Discount starts after filter ends -> exclude
          return false;
        }
      }
      
      return true;
    });
  }, [discounts, search, statusFilter, validFrom, validTo]);

  const toggleActive = async (id: string | number) => {
    // Extra security: Only Manager can toggle
    if (!isManager) return;
    
    // Find the discount being toggled
    const discountToToggle = discounts.find(d => d.id === id);
    if (!discountToToggle) return;
    
    const newActiveStatus = !discountToToggle.active;
    
    // Optimistically update the UI
    setDiscounts(prev => prev.map(d => d.id === id ? { ...d, active: newActiveStatus } : d));
    
    try {
      // Send the new is_active status along with the full discount payload
      console.log(`[DiscountManagement] Toggling discount ${id} to is_active=${newActiveStatus}`);
      
      // Extract the numeric value from the string (e.g., "50%" -> 50, "Rs. 150" -> 150)
      const valueStr = discountToToggle.value || '';
      const valueNum = discountToToggle.kind === 'percent' 
        ? Number(valueStr.replace('%', ''))
        : Number(valueStr.replace('Rs.', '').replace(/[^\d.]/g, ''));
      
      // Map UI discount type to API discount type
      const discountType = discountToToggle.kind === 'percent' ? 'Percentage' : 'FixedAmount';
      
      // Determine applicable_to and target IDs
      let applicableTo = 'All';
      let targetCategoryId = null;
      let targetProductId = null;
      
      if (discountToToggle.applicableTo !== 'All Items') {
        if (categories.includes(discountToToggle.applicableTo)) {
          applicableTo = 'Category';
          targetCategoryId = discountToToggle.applicableTo;
        } else {
          // Try to find matching product
          const matchingProduct = items.find(i => i.name === discountToToggle.applicableTo);
          if (matchingProduct) {
            applicableTo = 'Product';
            targetProductId = matchingProduct.id;
          }
        }
      }
      
      // Build complete payload with is_active
      const updateData: any = {
        name: discountToToggle.name,
        discount_type: discountType,
        value: valueNum,
        applicable_to: applicableTo,
        start_date: discountToToggle.startDate || null,
        end_date: discountToToggle.endDate || null,
        start_time: null,
        end_time: null,
        is_active: newActiveStatus,  // Add the status toggle
      };
      
      // Add target IDs if applicable
      if (targetCategoryId) {
        updateData.target_category_id = targetCategoryId;
        updateData.target_product_id = null;
      } else if (targetProductId) {
        updateData.target_product_id = targetProductId;
        updateData.target_category_id = null;
      } else {
        updateData.target_category_id = null;
        updateData.target_product_id = null;
      }
      
      console.log('[DiscountManagement] Toggling discount with payload:', updateData);
      
      await apiClient.discounts.update(id as number, updateData);
      
      console.log(`[DiscountManagement] Successfully toggled discount ${id} to is_active=${newActiveStatus}`);
    } catch (error) {
      // Revert the UI change on error
      console.error('[DiscountManagement] Error toggling discount status:', error);
      setDiscounts(prev => prev.map(d => d.id === id ? { ...d, active: !newActiveStatus } : d));
      
      const errorMsg = error instanceof Error ? error.message : 'Failed to toggle discount status';
      alert(`Failed to toggle discount status: ${errorMsg}`);
    }
  };

  const handleDelete = async () => {
    if (!discountToDelete) return;
    
    try {
      setIsDeleting(true);
      // Make API call to delete discount from backend
      await apiClient.discounts.delete(discountToDelete.id as number);
      
      // Update local state: remove the deleted discount
      setDiscounts(prev => prev.filter(d => d.id !== discountToDelete.id));
      
      // Close modals and reset state
      setDeleteConfirmOpen(false);
      setDiscountToDelete(null);
      
      console.log('[DiscountManagement] Discount deleted successfully:', discountToDelete.name);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to delete discount';
      console.error('[DiscountManagement] Error deleting discount:', error);
      alert(`Failed to delete discount: ${errorMsg}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const deleteSelected = () => {
    const sel = Object.keys(selected).filter(k => selected[k]);
    if (sel.length === 0) return;
    setDiscounts(prev => prev.filter(d => !sel.includes(String(d.id))));
    setSelected({});
  };

  const toggleSelect = (id: string | number) => {
    setSelected(s => ({ ...s, [String(id)]: !s[String(id)] }));
  };

  const activeCount = discounts.filter(d => d.active).length;

  return (
    <div className="p-6">
      <AddDiscountModal
        open={addDiscountOpen}
        onClose={() => setAddDiscountOpen(false)}
        onSave={async (discount) => {
          try {
            // Map UI types to API types
            const discountType = discount.type === 'percentage' ? 'Percentage' : 'FixedAmount';
            const applicableTo = discount.applicableTo === 'all' ? 'All' : discount.applicableTo === 'category' ? 'Category' : 'Product';
            
            // Prepare data for API
            const createData: any = {
              name: discount.name.trim(),
              discount_type: discountType,
              value: discount.value,
              applicable_to: applicableTo,
              start_date: discount.startDate || null,
              end_date: discount.endDate || null,
              start_time: discount.startTime || null,
              end_time: discount.endTime || null,
            };
            
            // Add target IDs based on applicable_to
            if (applicableTo === 'Category' && discount.category) {
              createData.target_category_id = discount.category;
              createData.target_product_id = null;
            } else if (applicableTo === 'Product' && discount.item) {
              createData.target_product_id = discount.item;
              createData.target_category_id = null;
            } else {
              createData.target_category_id = null;
              createData.target_product_id = null;
            }
            
            // Log payload for debugging
            console.log('[DiscountManagement] Creating discount with payload:', createData);
            
            // Make API call to save to database
            const response = await apiClient.discounts.create(createData);
            
            // Update local state only after successful API call
            setDiscounts(prev => [
              ...prev,
              {
                id: response.id,
                name: discount.name,
                kind: discount.type === 'percentage' ? 'percent' : 'fixed',
                value: discount.type === 'percentage' ? `${discount.value}%` : `Rs. ${discount.value}`,
                applicableTo:
                  discount.applicableTo === 'all'
                    ? 'All Items'
                    : discount.applicableTo === 'category'
                    ? discount.category
                    : items.find(i => i.id === discount.item)?.name || '',
                validity: formatValidityPeriod(discount.startDate || null, discount.endDate || null),
                startDate: discount.startDate || null,
                endDate: discount.endDate || null,
                active: true,
              },
            ]);
            
            // Close modal after successful save
            setAddDiscountOpen(false);
            console.log('[DiscountManagement] Discount created successfully:', response);
          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Failed to create discount';
            console.error('[DiscountManagement] Error creating discount:', error);
            alert(`Failed to create discount: ${errorMsg}`);
          }
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
            
            // Ensure dates are in YYYY-MM-DD format (or null)
            const formatDateForAPI = (dateStr: string | undefined): string | null => {
              if (!dateStr) return null;
              // If already in YYYY-MM-DD format, return as-is
              if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
              // Otherwise try to parse and reformat
              try {
                const date = new Date(dateStr);
                if (isNaN(date.getTime())) return null;
                return date.toISOString().split('T')[0];
              } catch {
                return null;
              }
            };
            
            // Prepare data for API
            const updateData: any = {
              name: updated.name,
              discount_type: discountType,
              value: updated.value,
              applicable_to: applicableTo,
              start_date: formatDateForAPI(updated.startDate),
              end_date: formatDateForAPI(updated.endDate),
              start_time: updated.startTime || null,
              end_time: updated.endTime || null,
            };
            
            // Log for debugging
            console.log('[DiscountManagement] Updating discount with payload:', updateData);
            
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
                    validity: formatValidityPeriod(updated.startDate || null, updated.endDate || null),
                    startDate: updated.startDate || null,
                    endDate: updated.endDate || null,
                  }
                : d
            ));
            setEditDiscountOpen(false);
            setEditingDiscount(null);
            console.log('[DiscountManagement] Discount updated successfully');
          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Failed to update discount';
            console.error('[DiscountManagement] Error updating discount:', error);
            alert(`Failed to update discount: ${errorMsg}. Please check the date format (must be YYYY-MM-DD).`);
          }
        }}
        categories={categories}
        items={items}
      />
      
      <DeleteConfirmationModal
        isOpen={deleteConfirmOpen}
        onClose={() => {
          setDeleteConfirmOpen(false);
          setDiscountToDelete(null);
        }}
        onConfirm={handleDelete}
        itemName={discountToDelete?.name || 'Discount'}
        isLoading={isDeleting}
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
                
                // Use raw dates from discount object (YYYY-MM-DD format)
                // Do NOT parse the formatted validity string
                const startDate = d.startDate || '';
                const endDate = d.endDate || '';

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
                        <button title="Delete" onClick={() => {
                          setDiscountToDelete(d);
                          setDeleteConfirmOpen(true);
                        }} className="p-2 rounded hover:bg-orange-100 text-red-500">
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