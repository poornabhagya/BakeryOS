import React, { useMemo, useState, useEffect } from 'react';
import { TrendingDown, Trash2, AlertCircle, Search, RotateCcw, Plus, Eye, Loader } from 'lucide-react';
import { Card } from './ui/card';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';
import { AddWastageReasonModal } from './modal/AddWastageReasonModal';
import { ViewWastageReasonsModal, WastageReason } from './modal/ViewWastageReasonsModal';
import { multiplyNumeric } from '../utils/numericUtils';
import { formatQuantityForDisplay } from '../utils/conversions';
import { wastageApi } from '../services/api';
import apiClient from '../services/api';
import { useAuth } from '../context/AuthContext';

type WastageItem = {
  id: string;
  name: string;
  category?: string;
  category_name?: string;
  reason: string;
  reasonId?: string;
  quantity: number;
  unit: string; // e.g., 'pcs', 'kg', 'L'
  trackingType?: string;
  unitCost: number; // per unit cost
  reportedBy: string;
  time: string; // e.g., '10:30 AM'
  date: string; // yyyy-mm-dd
};

export function WastageOverview() {
  const { user } = useAuth();
  const isManager = user?.role === 'Manager';
  const isStorekeeper = String(user?.role || '').toLowerCase() === 'storekeeper';
  const isCashier = String(user?.role || '').toLowerCase() === 'cashier';
  const canSeeProductData = !isStorekeeper;
  const canSeeIngredientData = !isCashier;

  const today = new Date().toISOString().slice(0,10);
  const [dateFrom, setDateFrom] = useState<string>('1970-01-01'); // All Time default
  const [dateTo, setDateTo] = useState<string>(today);
  const [timePeriod, setTimePeriod] = useState<string>('All Time');
  const [reasonId, setReasonId] = useState<string>('All Reasons');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const [addReasonOpen, setAddReasonOpen] = useState(false);
  const [viewReasonsOpen, setViewReasonsOpen] = useState(false);
  const [wastageReasons, setWastageReasons] = useState<WastageReason[]>([]);

  const [productWastage, setProductWastage] = useState<WastageItem[]>([]);
  const [ingredientWastage, setIngredientWastage] = useState<WastageItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isExportingExcel, setIsExportingExcel] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Fetch wastage data from API
  useEffect(() => {
    const fetchWastageData = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);

        const [response, ingredientsResponse, reasonsResponse] = await Promise.all([
          wastageApi.getAll(),
          apiClient.ingredients.getAllPages(),
          apiClient.wastageReason.getAll(),
        ]);

        // Process wastage reasons
        const mappedReasons = (reasonsResponse || []).map((reason: any) => ({
          id: reason.id?.toString() || '',
          name: reason.reason || reason.name || '',
          note: reason.description || reason.note || '',
        }));
        setWastageReasons(mappedReasons);

        const ingredientTrackingById = new Map<number, string>();
        (ingredientsResponse?.items || []).forEach((ing: any) => {
          ingredientTrackingById.set(Number(ing.id), String(ing.tracking_type || ''));
        });

        const wastageItems = Array.isArray(response)
          ? response
          : (Array.isArray((response as any)?.items)
              ? (response as any).items
              : ((response as any)?.results || (response as any)?.data || []));

        console.log('Wastage API Response:', JSON.stringify(response, null, 2));
        console.log('Wastage Items:', wastageItems);

        // Separate product wastage (IDs like 'PW-001') from ingredient wastage (IDs like 'IW-001')
        const products: WastageItem[] = [];
        const ingredients: WastageItem[] = [];

        wastageItems.forEach((item: any) => {
          const wastageId = item.wastage_id || '';
          
          console.log('Processing item:', { wastageId, item });

          // Transform API response to WastageItem format
          // Backend returns: product_name, ingredient_name, reason_text, reported_by_name
          const transformedItem: WastageItem = {
            id: wastageId,
            name: item.product_name || item.ingredient_name || 'Unknown',
            category: item.category_name,
            category_name: item.category_name,
            reason: item.reason_text || 'Unknown',
            reasonId: item.reason_id?.toString(),
            quantity: item.quantity || 0,
            unit: 'Unit', // Default unit, adjust if API provides units
            trackingType: ingredientTrackingById.get(Number(item.ingredient_id)) || undefined,
            unitCost: item.unit_cost || 0,
            reportedBy: item.reported_by_name || 'System',
            time: new Date(item.created_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            date: new Date(item.created_at).toISOString().slice(0, 10),
          };

          console.log('Transformed item:', transformedItem);

          // Distinguish product vs ingredient wastage by ID prefix
          if (wastageId.startsWith('PW')) {
            console.log('Adding to products:', transformedItem);
            products.push(transformedItem);
          } else if (wastageId.startsWith('IW')) {
            console.log('Adding to ingredients:', transformedItem);
            ingredients.push(transformedItem);
          } else {
            console.warn('Unknown wastage ID prefix:', wastageId);
          }
        });

        console.log('Final products:', products);
        console.log('Final ingredients:', ingredients);

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
      if (reasonId !== 'All Reasons' && i.reasonId !== reasonId) return false;
      if (searchTerm.trim()) {
        const q = searchTerm.trim().toLowerCase();
        if (!i.name.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [productWastage, dateFrom, dateTo, reasonId, searchTerm]);

  const filteredIngredient = useMemo(() => {
    return ingredientWastage.filter((i) => {
      if (i.date < dateFrom || i.date > dateTo) return false;
      if (reasonId !== 'All Reasons' && i.reasonId !== reasonId) return false;
      if (searchTerm.trim()) {
        const q = searchTerm.trim().toLowerCase();
        if (!i.name.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [ingredientWastage, dateFrom, dateTo, reasonId, searchTerm]);

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
    setDateFrom('1970-01-01'); // Reset to All Time
    setDateTo(todayIso);
    setTimePeriod('All Time');
    setReasonId('All Reasons');
    setSearchTerm('');
  };

  // KPIs - Separate calculations for products and ingredients
  const kpiStats = useMemo(() => {
    // Total Loss
    const productLoss = filteredProduct.reduce((s, it) => s + multiplyNumeric(it.unitCost, it.quantity), 0);
    const ingredientLoss = filteredIngredient.reduce((s, it) => s + multiplyNumeric(it.unitCost, it.quantity), 0);

    // Total Quantity (using Number() to prevent string concatenation)
    const productQty = filteredProduct.reduce((s, it) => s + Number(it.quantity), 0);
    const ingredientQty = filteredIngredient.reduce((s, it) => s + Number(it.quantity), 0);

    // Most Wasted Item (separately)
    const mostWastedProduct = filteredProduct.length > 0 
      ? filteredProduct.reduce((max, it) => (Number(it.quantity) > Number(max?.quantity ?? -1) ? it : max), filteredProduct[0])
      : null;

    const mostWastedIngredient = filteredIngredient.length > 0
      ? filteredIngredient.reduce((max, it) => (Number(it.quantity) > Number(max?.quantity ?? -1) ? it : max), filteredIngredient[0])
      : null;

    return {
      productLoss,
      ingredientLoss,
      productQty,
      ingredientQty,
      mostWastedProduct,
      mostWastedIngredient
    };
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

  const formatWholeItemQuantity = (value: number) => {
    const num = Number(value);
    if (!Number.isFinite(num)) return '0';
    if (Number.isInteger(num)) return String(num);
    return num.toFixed(2).replace(/\.0+$/, '').replace(/(\.\d*[1-9])0+$/, '$1');
  };

  const exportToPDF = () => {
    try {
      if (filteredProduct.length === 0 && filteredIngredient.length === 0) {
        alert('No wastage data to export');
        return;
      }

      // Create new PDF document
      const pdf = new jsPDF();
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 15;
      let currentY = 15;

      // --- HEADER SECTION ---
      // Title
      pdf.setFontSize(18);
      pdf.setTextColor(0, 100, 0);
      pdf.text('BakeryOS - Wastage Report', margin, currentY);
      currentY += 7;

      // Subtitle with generation date/time
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      const generatedDate = new Date().toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
      pdf.text(`Generated: ${generatedDate}`, margin, currentY);
      currentY += 7;

      // Date Range Info
      pdf.setFontSize(10);
      pdf.setTextColor(80, 80, 80);
      const dateRangeText = `Date Range: ${dateFrom} to ${dateTo}`;
      pdf.text(dateRangeText, margin, currentY);
      currentY += 12;

      // --- PRODUCT WASTAGE TABLE ---
      if (filteredProduct.length > 0) {
        // Section Title
        pdf.setFontSize(12);
        pdf.setTextColor(0, 100, 0);
        pdf.text('Product Wastage', margin, currentY);
        currentY += 6;

        // Prepare product table rows
        const productTableRows = filteredProduct.map((item) => [
          item.name,
          item.category_name || 'Unknown',
          item.reason,
          `${item.quantity} ${item.unit}`,
          `Rs. ${multiplyNumeric(item.unitCost, item.quantity).toLocaleString()}`,
          item.reportedBy,
          formatDateDisplay(item.date, item.time)
        ]);

        // Calculate product totals
        const productTotalLoss = filteredProduct.reduce(
          (sum, item) => sum + multiplyNumeric(item.unitCost, item.quantity),
          0
        );

        // Add product summary row
        const productSummaryRow = [
          'TOTAL',
          '',
          '',
          '',
          `Rs. ${productTotalLoss.toLocaleString()}`,
          '',
          ''
        ];

        // Generate product table
        autoTable(pdf, {
          startY: currentY,
          head: [['Item Name', 'Category', 'Reason', 'Quantity', 'Loss Amount', 'Reported By', 'Date & Time']],
          body: productTableRows,
          foot: [productSummaryRow],
          headStyles: {
            fillColor: [0, 100, 0],
            textColor: [255, 255, 255],
            fontStyle: 'bold',
            halign: 'center',
            valign: 'middle'
          },
          bodyStyles: {
            textColor: [40, 40, 40],
            lineColor: [200, 200, 200]
          },
          footStyles: {
            fillColor: [240, 240, 240],
            textColor: [0, 0, 0],
            fontStyle: 'bold',
            lineColor: [0, 100, 0],
            lineWidth: 1
          },
          columnStyles: {
            0: { halign: 'left' },
            1: { halign: 'left' },
            2: { halign: 'center' },
            3: { halign: 'center' },
            4: { halign: 'right' },
            5: { halign: 'left' },
            6: { halign: 'left' }
          },
          margin: { left: margin, right: margin, top: margin, bottom: margin }
        });

        currentY = (pdf as any).lastAutoTable.finalY + 10;
      }

      // --- INGREDIENT WASTAGE TABLE ---
      if (filteredIngredient.length > 0) {
        // Add page break if needed
        if (currentY > 250) {
          pdf.addPage();
          currentY = 15;
        }

        // Section Title
        pdf.setFontSize(12);
        pdf.setTextColor(0, 100, 0);
        pdf.text('Ingredient Wastage', margin, currentY);
        currentY += 6;

        // Prepare ingredient table rows
        const ingredientTableRows = filteredIngredient.map((item) => [
          item.name,
          item.category_name || 'Unknown',
          item.reason,
          `${item.quantity} ${item.unit}`,
          `Rs. ${multiplyNumeric(item.unitCost, item.quantity).toLocaleString()}`,
          item.reportedBy,
          formatDateDisplay(item.date, item.time)
        ]);

        // Calculate ingredient totals
        const ingredientTotalLoss = filteredIngredient.reduce(
          (sum, item) => sum + multiplyNumeric(item.unitCost, item.quantity),
          0
        );

        // Add ingredient summary row
        const ingredientSummaryRow = [
          'TOTAL',
          '',
          '',
          '',
          `Rs. ${ingredientTotalLoss.toLocaleString()}`,
          '',
          ''
        ];

        // Generate ingredient table
        autoTable(pdf, {
          startY: currentY,
          head: [['Item Name', 'Category', 'Reason', 'Quantity', 'Loss Amount', 'Reported By', 'Date & Time']],
          body: ingredientTableRows,
          foot: [ingredientSummaryRow],
          headStyles: {
            fillColor: [0, 100, 0],
            textColor: [255, 255, 255],
            fontStyle: 'bold',
            halign: 'center',
            valign: 'middle'
          },
          bodyStyles: {
            textColor: [40, 40, 40],
            lineColor: [200, 200, 200]
          },
          footStyles: {
            fillColor: [240, 240, 240],
            textColor: [0, 0, 0],
            fontStyle: 'bold',
            lineColor: [0, 100, 0],
            lineWidth: 1
          },
          columnStyles: {
            0: { halign: 'left' },
            1: { halign: 'left' },
            2: { halign: 'center' },
            3: { halign: 'center' },
            4: { halign: 'right' },
            5: { halign: 'left' },
            6: { halign: 'left' }
          },
          margin: { left: margin, right: margin, top: margin, bottom: margin },
          didDrawPage: (data) => {
            // Add page number at bottom
            const pageSize = pdf.internal.pageSize;
            const pageHeight = pageSize.getHeight();
            const pageCount = (pdf as any).getNumberOfPages();
            const pageNum = data.pageNumber;
            pdf.setFontSize(9);
            pdf.setTextColor(150, 150, 150);
            pdf.text(`Page ${pageNum} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
          }
        });
      }

      // Save PDF with timestamp
      const timestamp = new Date().toISOString().slice(0, 10);
      pdf.save(`wastage-report-${timestamp}.pdf`);
    } catch (error) {
      console.error('[WastageOverview] Error exporting PDF:', error);
      alert('Failed to export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      if (filteredProduct.length === 0 && filteredIngredient.length === 0) {
        alert('No wastage data to export');
        return;
      }

      setIsExportingExcel(true);
      const selectedReasonText = reasonId === 'All Reasons' ? 'All Reasons' : wastageReasons.find(r => r.id === reasonId)?.name || 'All Reasons';
      const { blob, fileName } = await wastageApi.exportExcel({
        search: searchTerm.trim() || undefined,
        date_from: dateFrom,
        date_to: dateTo,
        time_period: timePeriod,
        reason: selectedReasonText,
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('[WastageOverview] Error exporting Excel:', error);
      alert('Failed to export Excel');
    } finally {
      setIsExportingExcel(false);
    }
  };

  // Handler for adding a new reason (called after successful API submission)
  const handleAddWastageReason = (reason: WastageReason) => {
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
        onSuccess={handleAddWastageReason}
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
            {/* Total Loss Today */}
            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
              <div className="p-3 rounded bg-white text-red-500">
                <TrendingDown className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-red-800 font-semibold">Total Loss Today</div>
                {canSeeProductData && (
                  <div className="text-lg font-bold text-red-600">
                    Rs. {kpiStats.productLoss.toLocaleString()} (Products)
                  </div>
                )}
                {canSeeIngredientData && (
                  <div className="text-lg font-bold text-red-600">
                    Rs. {kpiStats.ingredientLoss.toLocaleString()} (Ingredients)
                  </div>
                )}
              </div>
            </div>

            {/* Total Wasted Qty */}
            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
              <div className="p-3 rounded bg-white text-orange-500">
                <Trash2 className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-orange-800 font-semibold">Total Wasted Qty</div>
                {canSeeProductData && (
                  <div className="text-lg font-bold text-orange-700">
                    {kpiStats.productQty} (Products)
                  </div>
                )}
                {canSeeIngredientData && (
                  <div className="text-lg font-bold text-orange-700">
                    {kpiStats.ingredientQty} (Ingredients)
                  </div>
                )}
              </div>
            </div>

            {/* Most Wasted Item */}
            <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
              <div className="p-3 rounded bg-white text-blue-500">
                <AlertCircle className="w-5 h-5" />
              </div>
              <div>
                <div className="text-sm text-blue-800 font-semibold">Most Wasted Item</div>
                {canSeeProductData && kpiStats.mostWastedProduct && (
                  <div className="text-sm font-semibold text-blue-700">
                    {kpiStats.mostWastedProduct.name} ({Number(kpiStats.mostWastedProduct.quantity).toLocaleString()} {kpiStats.mostWastedProduct.unit}) - Product
                  </div>
                )}
                {canSeeIngredientData && kpiStats.mostWastedIngredient && (
                  <div className="text-sm font-semibold text-blue-700">
                    {kpiStats.mostWastedIngredient.name} ({Number(kpiStats.mostWastedIngredient.quantity).toLocaleString()} {kpiStats.mostWastedIngredient.unit}) - Ingredient
                  </div>
                )}
                {((canSeeProductData && !kpiStats.mostWastedProduct) && (canSeeIngredientData && !kpiStats.mostWastedIngredient)) && (
                  <div className="text-lg font-bold text-blue-700">—</div>
                )}
                {(!canSeeProductData && canSeeIngredientData && !kpiStats.mostWastedIngredient) && (
                  <div className="text-lg font-bold text-blue-700">—</div>
                )}
                {(canSeeProductData && !canSeeIngredientData && !kpiStats.mostWastedProduct) && (
                  <div className="text-lg font-bold text-blue-700">—</div>
                )}
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

              <select value={reasonId} onChange={(e) => setReasonId(e.target.value)} className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900">
                <option value="All Reasons">All Reasons</option>
                {wastageReasons.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>

              <button onClick={resetFilters} className="ml-2 text-red-500 hover:text-red-700 flex items-center gap-1 font-medium text-sm">
                  <RotateCcw className="w-4 h-4" /> Reset Filters
                </button>            

              <div className="relative ml-auto flex items-center gap-3">

                {isManager && (
                  <>
                    <button onClick={exportToPDF} className="ml-2 px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors">
                      Export PDF
                    </button>

                    <button
                      onClick={exportToExcel}
                      disabled={isExportingExcel}
                      style={{ backgroundColor: '#16a34a', color: '#ffffff', borderColor: '#15803d' }}
                      className="px-4 py-2 rounded-lg font-bold shadow-md hover:opacity-90 disabled:opacity-60 disabled:cursor-not-allowed flex items-center gap-2 transition-opacity border"
                    >
                      {isExportingExcel ? <Loader className="w-4 h-4 animate-spin" /> : null}
                      <span style={{ color: '#ffffff' }}>Export Excel</span>
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
                  </>
                )}

                
              </div>
            </div>
          </div>

          {/* Dual Tables Grid */}
          <div className={`grid grid-cols-1 ${(canSeeProductData && canSeeIngredientData) ? 'xl:grid-cols-2' : ''} gap-6`}>
            {/* Product Wastage Table */}
            {canSeeProductData && (
              <div className="bg-white rounded-lg border border-orange-100 overflow-hidden wastage-table">
              <div className="rounded-t-lg bg-orange-100 p-4 flex items-center justify-between">
                  <h4 className="font-semibold text-orange-700">Product Wastage</h4>
                </div>
                <div className="p-4 overflow-auto">
                {/* Loading State */}
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="spinner mb-4 mx-auto w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
                      <p className="text-gray-600 text-sm">Loading product wastage...</p>
                    </div>
                  </div>
                ) : filteredProduct.length === 0 ? (
                  /* Empty State */
                  <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                    <svg className="w-12 h-12 mb-3 text-orange-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-gray-600 font-medium">No product wastage records found</p>
                    <p className="text-gray-400 text-sm">Products wasted will appear here</p>
                  </div>
                ) : (
                  /* Data Table */
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
                          <td className="py-3 px-4 text-gray-600">{r.category || r.category_name || 'Unknown'}</td>
                          <td className="py-3 px-4"> <span className={reasonBadge(r.reason)}>{r.reason}</span> </td>
                          <td className="py-3 px-4 text-gray-800">{formatWholeItemQuantity(r.quantity)} {r.unit}</td>
                          <td className="py-3 px-4 text-red-700">Rs. {multiplyNumeric(r.unitCost, r.quantity).toLocaleString()}</td>
                          <td className="py-3 px-4 text-gray-600">{r.reportedBy}</td>
                          <td className="py-3 px-4 text-gray-600">{formatDateDisplay(r.date, r.time)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              </div>
            )}

            {/* Ingredient Wastage Table */}
            {canSeeIngredientData && (
              <div className="bg-white rounded-lg border border-orange-100 overflow-hidden wastage-table">
              <div className="rounded-t-lg bg-orange-100 p-4 flex items-center justify-between">
                  <h4 className="font-semibold text-orange-700">Ingredient Wastage</h4>
                </div>
                <div className="p-4 overflow-auto">
                {/* Loading State */}
                {isLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <div className="spinner mb-4 mx-auto w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin"></div>
                      <p className="text-gray-600 text-sm">Loading ingredient wastage...</p>
                    </div>
                  </div>
                ) : filteredIngredient.length === 0 ? (
                  /* Empty State */
                  <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                    <svg className="w-12 h-12 mb-3 text-orange-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                    <p className="text-gray-600 font-medium">No ingredient wastage records found</p>
                    <p className="text-gray-400 text-sm">Wasted ingredients will appear here</p>
                  </div>
                ) : (
                  /* Data Table */
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
                          <td className="py-3 px-4 text-gray-600">{r.category || r.category_name || 'Unknown'}</td>
                          <td className="py-3 px-4"> <span className={reasonBadge(r.reason)}>{r.reason}</span> </td>
                          <td className="py-3 px-4 text-gray-800">{formatQuantityForDisplay(r.quantity, r.trackingType || 'Count')}</td>
                          <td className="py-3 px-4 text-red-700">Rs. {multiplyNumeric(r.unitCost, r.quantity).toLocaleString()}</td>
                          <td className="py-3 px-4 text-gray-600">{r.reportedBy}</td>
                          <td className="py-3 px-4 text-gray-600">{formatDateDisplay(r.date, r.time)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
              </div>
            )}
          </div>
        </>
      )}
    </Card>
  );
}
