import React, { useMemo, useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Banknote, ReceiptText, TrendingUp, Eye, Printer, Search, RotateCcw, Loader } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import html2canvas from 'html2canvas';
import { toNumber } from '../utils/numericUtils';
import apiClient from '../services/api';
import { convertApiSaleToUi } from '../utils/conversions';
import { ViewSaleModal } from './modal/ViewSaleModal';
import { useAuth } from '../context/AuthContext';

type SaleItem = {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
};

type Sale = {
  id: number;                      // integer PK
  bill_number: string;             // "BILL-1001"
  cashier_id: number;
  cashier_name: string;
  subtotal: number;
  discount_id: number | null;
  discount_name?: string | null;
  discount_amount: number;
  total_amount: number;            // Renamed from 'total'
  payment_method: string;
  item_count: number;
  date_time: string;               // ISO datetime string
  created_at: string;
  items?: SaleItem[];               // Nested sale items for detail view
};

export function SalesSummary() {
  const { user } = useAuth();
  const isManager = user?.role === 'Manager';

  // --- State: API Data ---
  const [sales, setSales] = useState<Sale[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // --- Fetch Sales from API ---
  useEffect(() => {
    const fetchSales = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);
        const response = await apiClient.sales.getAll();
        // response.items already contains UI-formatted sales - empty array if no sales
        setSales(response.items || []);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch sales';
        setFetchError(errorMsg);
        console.error('Error fetching sales:', error);
        // On error, set to empty array - don't use mock data
        setSales([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSales();
  }, []);
  const today = new Date().toISOString().slice(0,10);
  const defaultFrom = new Date(1970,0,1).toISOString().slice(0,10);
  const [timePeriod, setTimePeriod] = useState<string>('All Time');
  const [dateFrom, setDateFrom] = useState<string>(defaultFrom);
  const [dateTo, setDateTo] = useState<string>(today);
  const [searchId, setSearchId] = useState<string>('');
  const [amountFilter, setAmountFilter] = useState<string>('All');

  // --- State: Modal & Reprint ---
  const [viewSaleModal, setViewSaleModal] = useState<{ open: boolean; sale: Sale | null }>({ open: false, sale: null });
  const [isLoadingSaleDetail, setIsLoadingSaleDetail] = useState(false);
  const [isExportingExcel, setIsExportingExcel] = useState(false);

  const filtered = useMemo(() => {
    // Filter from REAL sales data, not mock
    return sales.filter(s => {
      const saleDate = new Date(s.date_time).toISOString().slice(0, 10);
      // Proper date range filtering: check if sale date is >= dateFrom AND <= dateTo
      if (saleDate < dateFrom || saleDate > dateTo) return false;
      if (searchId.trim() && !s.bill_number.toLowerCase().includes(searchId.trim().toLowerCase())) return false;
      // Safely compare total_amount that might come as string from API
      if (amountFilter === 'High' && toNumber(s.total_amount) <= 1000) return false;
      return true;
    });
  }, [sales, dateFrom, dateTo, searchId, amountFilter]);

  const applyTimePeriod = (period: string) => {
    const now = new Date();
    let start = new Date();
    let end = new Date();

    if (period === 'All Time') {
      // All time: from 1970 to today at end of day
      start = new Date(1970, 0, 1);
      end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    } else if (period === 'Today') {
      // Today: from start of today to end of today
      start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
      end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    } else if (period === 'Yesterday') {
      // Yesterday: from start of yesterday to end of yesterday
      const yesterday = new Date(now);
      yesterday.setDate(now.getDate() - 1);
      start = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 0, 0, 0);
      end = new Date(yesterday.getFullYear(), yesterday.getMonth(), yesterday.getDate(), 23, 59, 59);
    } else if (period === 'This Week') {
      // This week: from Sunday (or Monday depending on locale) to today at end of day
      const dayOfWeek = now.getDay();
      // Start of week (Sunday = 0)
      const daysToSubtract = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // Monday is start of week
      const weekStart = new Date(now);
      weekStart.setDate(now.getDate() - daysToSubtract);
      start = new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate(), 0, 0, 0);
      end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    } else if (period === 'This Month') {
      // This month: from 1st of this month to end of today (or last day if today is not month end)
      start = new Date(now.getFullYear(), now.getMonth(), 1, 0, 0, 0);
      end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    }

    // Convert to ISO date strings (YYYY-MM-DD format)
    const toIso = (d: Date) => d.toISOString().slice(0, 10);
    setDateFrom(toIso(start));
    setDateTo(toIso(end));
  };

  const totalRevenue = useMemo(() => {
    // Safely convert total_amount that might be strings from backend API
    return filtered.reduce((sum, s) => sum + toNumber(s.total_amount), 0);
  }, [filtered]);
  const totalTransactions = filtered.length;
  const avgOrder = totalTransactions ? Math.round(toNumber(totalRevenue) / totalTransactions) : 0;

  const formatDateTime = (dateTimeStr: string) => {
    const d = new Date(dateTimeStr);
    const datePart = d.toLocaleString('en-US', { month: 'short', day: 'numeric' });
    const timePart = d.toLocaleString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    return `${datePart}, ${timePart}`;
  };

  const resetFilters = () => {
    // Reset all filters to their initial default values
    const todayIso = new Date().toISOString().slice(0,10);
    const defaultFromIso = new Date(1970,0,1).toISOString().slice(0,10);
    
    setTimePeriod('All Time');      // Reset time period to "All Time"
    setSearchId('');                 // Clear search input
    setDateFrom(defaultFromIso);     // Reset start date to 1970-01-01 (all time)
    setDateTo(todayIso);             // Reset end date to today
    setAmountFilter('All');          // Reset amount filter to "All"
  };

  const exportToPDF = () => {
    try {
      if (filtered.length === 0) {
        alert('No sales data to export');
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
      pdf.text('BakeryOS - Sales Report', margin, currentY);
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
      currentY += 10;

      // --- TABLE DATA ---
      // Prepare table rows from filtered sales
      const tableRows = filtered.map((sale) => [
        sale.bill_number,
        new Date(sale.date_time).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }),
        sale.cashier_name,
        sale.payment_method,
        `Rs. ${toNumber(sale.subtotal).toFixed(2)}`,
        `Rs. ${toNumber(sale.discount_amount).toFixed(2)}`,
        `Rs. ${toNumber(sale.total_amount).toFixed(2)}`
      ]);

      // Calculate totals
      const totalSubtotal = filtered.reduce((sum, s) => sum + toNumber(s.subtotal), 0);
      const totalDiscount = filtered.reduce((sum, s) => sum + toNumber(s.discount_amount), 0);
      const totalAmount = filtered.reduce((sum, s) => sum + toNumber(s.total_amount), 0);

      // Add summary row
      const summaryRow = [
        'TOTAL',
        '',
        '',
        '',
        `Rs. ${totalSubtotal.toFixed(2)}`,
        `Rs. ${totalDiscount.toFixed(2)}`,
        `Rs. ${totalAmount.toFixed(2)}`
      ];

      // Generate table using autoTable
      autoTable(pdf, {
        startY: currentY,
        head: [['Bill Number', 'Date & Time', 'Cashier Name', 'Payment Method', 'Subtotal', 'Discount Amount', 'Final Total']],
        body: tableRows,
        foot: [summaryRow],
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
          1: { halign: 'center' },
          2: { halign: 'left' },
          3: { halign: 'center' },
          4: { halign: 'right' },
          5: { halign: 'right' },
          6: { halign: 'right' }
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

      // Save PDF with timestamp
      const timestamp = new Date().toISOString().slice(0, 10);
      pdf.save(`sales-report-${timestamp}.pdf`);
    } catch (error) {
      console.error('[SalesSummary] Error exporting PDF:', error);
      alert('Failed to export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      setIsExportingExcel(true);
      const { blob, fileName } = await apiClient.sales.exportExcel({
        start_date: dateFrom,
        end_date: dateTo,
        search: searchId.trim(),
        amount_filter: amountFilter,
      });

      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = fileName;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('[SalesSummary] Error exporting Excel:', error);
      alert('Failed to export Excel');
    } finally {
      setIsExportingExcel(false);
    }
  };

  // --- Handler: View Sale Details ---
  const handleViewSale = async (sale: Sale) => {
    try {
      setIsLoadingSaleDetail(true);
      // Fetch detailed sale including nested items
      const detailedSale = await apiClient.sales.getSale(sale.id);
      setViewSaleModal({ open: true, sale: detailedSale });
      console.log('[SalesSummary] Sale detail loaded:', detailedSale.bill_number);
    } catch (error) {
      console.error('[SalesSummary] Error fetching sale details:', error);
      alert('Failed to load sale details');
    } finally {
      setIsLoadingSaleDetail(false);
    }
  };

  // --- Handler: Reprint Receipt ---
  const handleReprintReceipt = async (sale: Sale) => {
    try {
      // Fetch detailed sale including nested items for receipt
      const detailedSale = await apiClient.sales.getSale(sale.id);

      // Build receipt HTML (same format as BillingScreen)
      const receiptHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: monospace;
              line-height: 1.6;
              background: white;
              color: black;
              padding: 20px;
            }
            .bill-header {
              text-align: center;
              margin-bottom: 20px;
              border-bottom: 1px solid #ddd;
              padding-bottom: 10px;
            }
            .bill-header h2 {
              margin: 0;
              font-size: 18px;
              font-weight: bold;
            }
            .bill-header p {
              margin: 5px 0;
              font-size: 12px;
            }
            .bill-meta {
              margin-bottom: 15px;
              font-size: 12px;
            }
            .bill-meta-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
            }
            .divider {
              border-top: 1px solid #ddd;
              margin: 15px 0;
            }
            table {
              width: 100%;
              margin-bottom: 15px;
              font-size: 12px;
              border-collapse: collapse;
            }
            thead {
              border-bottom: 1px solid #ddd;
            }
            th {
              text-align: left;
              padding-bottom: 5px;
              font-weight: bold;
            }
            td {
              padding: 5px 0;
              border-bottom: 1px solid #eee;
            }
            .qty-col {
              text-align: center;
            }
            .price-col {
              text-align: right;
            }
            .total-col {
              text-align: right;
            }
            .bill-totals {
              font-size: 12px;
              margin-bottom: 15px;
            }
            .total-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
            }
            .discount-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
              color: #28a745;
            }
            .final-total {
              display: flex;
              justify-content: space-between;
              margin-top: 10px;
              padding-top: 10px;
              border-top: 1px solid #ddd;
              font-weight: bold;
              font-size: 14px;
            }
            .bill-footer {
              text-align: center;
              margin-top: 20px;
              font-size: 11px;
              border-top: 1px solid #ddd;
              padding-top: 10px;
            }
            .bill-footer p {
              margin: 5px 0;
              color: #666;
            }
          </style>
        </head>
        <body>
          <div class="bill-header">
            <h2>BakeryOS</h2>
            <p>Manager Portal - Receipt</p>
          </div>

          <div class="bill-meta">
            <div class="bill-meta-row">
              <span>Bill Number:</span>
              <span style="font-weight: bold;">${detailedSale.bill_number}</span>
            </div>
            <div class="bill-meta-row">
              <span>Date:</span>
              <span>${new Date(detailedSale.date_time).toLocaleString()}</span>
            </div>
            <div class="bill-meta-row">
              <span>Cashier:</span>
              <span>${detailedSale.cashier_name || 'N/A'}</span>
            </div>
            <div class="bill-meta-row">
              <span>Payment:</span>
              <span>${detailedSale.payment_method || 'Cash'}</span>
            </div>
          </div>

          <div class="divider"></div>

          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th class="qty-col">Qty</th>
                <th class="price-col">Price</th>
                <th class="total-col">Total</th>
              </tr>
            </thead>
            <tbody>
              ${detailedSale.items?.map((item: SaleItem) => `
                <tr>
                  <td>${item.product_name}</td>
                  <td class="qty-col">${item.quantity}</td>
                  <td class="price-col">Rs. ${toNumber(item.unit_price).toLocaleString()}</td>
                  <td class="total-col">Rs. ${toNumber(item.subtotal).toLocaleString()}</td>
                </tr>
              `).join('') || ''}
            </tbody>
          </table>

          <div class="divider"></div>

          <div class="bill-totals">
            <div class="total-row">
              <span>Subtotal:</span>
              <span>Rs. ${toNumber(detailedSale.subtotal).toLocaleString()}</span>
            </div>
            ${detailedSale.discount_amount > 0 ? `
              <div class="discount-row">
                <span>Discount ${detailedSale.discount_name ? `(${detailedSale.discount_name})` : ''}:</span>
                <span>-Rs. ${toNumber(detailedSale.discount_amount).toLocaleString()}</span>
              </div>
            ` : ''}
            <div class="final-total">
              <span>Total:</span>
              <span>Rs. ${toNumber(detailedSale.total_amount).toLocaleString()}</span>
            </div>
          </div>

          <div class="bill-footer">
            <p>Thank you for your purchase!</p>
            <p>Printed: ${new Date().toLocaleString()}</p>
          </div>
        </body>
        </html>
      `;

      // Open print dialog
      const printWindow = window.open('', '', 'height=800,width=600');
      if (!printWindow) {
        throw new Error('Failed to open print window');
      }

      printWindow.document.write(receiptHTML);
      printWindow.document.close();

      // Wait for content to render, then trigger print
      setTimeout(() => {
        printWindow.print();
        console.log('[SalesSummary] Print dialog opened:', detailedSale.bill_number);
      }, 500);
    } catch (error) {
      console.error('[SalesSummary] Error reprinting receipt:', error);
      alert('Failed to reprint receipt');
    }
  };

  return (
    <div className="p-6">
      {/* Error Message */}
      {fetchError && (
        <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
          <p className="font-semibold">Error loading sales data</p>
          <p className="text-sm">{fetchError}</p>
        </div>
      )}
      
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 border border-green-200" style={{ backgroundColor: '#ecfdf5' }}>
          <div className="p-3 rounded bg-white text-green-500">
            <Banknote className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-green-800 font-semibold">Total Revenue (Today)</div>
            <div className="text-lg font-bold text-green-600">Rs. {totalRevenue.toLocaleString()}</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 border border-blue-200" style={{ backgroundColor: '#eff6ff' }}>
          <div className="p-3 rounded bg-white text-blue-500">
            <ReceiptText className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-blue-800 font-semibold">Total Transactions</div>
            <div className="text-lg font-bold text-blue-700">{totalTransactions} Orders</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 border border-purple-200" style={{ backgroundColor: '#f5f3ff' }}>
          <div className="p-3 rounded bg-white text-purple-500">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-purple-800 font-semibold">Average Order Value</div>
            <div className="text-lg font-bold text-purple-700">Rs. {avgOrder.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm mb-6 flex flex-wrap gap-4 items-center">

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-green-300 w-4 h-4" />
          <input value={searchId} onChange={(e) => setSearchId(e.target.value)} placeholder="Search by Bill ID (e.g. #108)..." className="pl-10 px-4 py-2 rounded-lg border border-gray-100 bg-green-50 text-green-900 w-64" />
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Time Period</label>
          <select value={timePeriod} onChange={(e) => { setTimePeriod(e.target.value); applyTimePeriod(e.target.value); }} className="px-4 py-2 rounded-lg border border-gray-100 bg-green-50 text-green-900">
            <option>All Time</option>
            <option>Today</option>
            <option>Yesterday</option>
            <option>This Week</option>
            <option>This Month</option>
          </select>
        </div>

        

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Date Range</label>
          <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setTimePeriod('Custom'); }} className="px-3 py-2 rounded-lg border border-gray-100 bg-green-50 text-green-900" />
          <span className="text-gray-400">to</span>
          <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setTimePeriod('Custom'); }} className="px-3 py-2 rounded-lg border border-gray-100 bg-green-50 text-green-900" />
        </div>

        <select value={amountFilter} onChange={(e) => setAmountFilter(e.target.value)} className="px-4 py-2 rounded-lg border border-gray-100 bg-green-50 text-green-900">
          <option value="All">All</option>
          <option value="High">High Value Bills (&gt; Rs. 1000)</option>
        </select>

        <div className="ml-auto flex items-center gap-4">
          <button onClick={resetFilters} className="text-gray-500 hover:text-gray-700 flex items-center gap-2 font-medium">
            <RotateCcw className="w-4 h-4" /> Reset
          </button>

          {isManager && (
            <>
              <button onClick={exportToPDF} className="px-4 py-2 rounded-lg bg-red-600 text-white font-bold shadow-md hover:bg-red-700 flex items-center gap-2 transition-colors border border-red-700">
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
            </>
          )}
        </div>
      </div>

      {/* Sales Table */}
      <div className="bg-white rounded-lg border border-green-100 overflow-hidden sales-table">
        <div className="rounded-t-lg bg-green-100 p-4 flex items-center justify-between">
          <h4 className="font-semibold text-green-800">Sales History</h4>
        </div>
        <div className="p-4 overflow-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-green-900">
                <th className="py-3 px-4 font-semibold border-b border-green-100">Bill ID</th>
                <th className="py-3 px-4 font-semibold border-b border-green-100">Date & Time</th>
                <th className="py-3 px-4 font-semibold border-b border-green-100">Items Summary</th>
                <th className="py-3 px-4 font-semibold border-b border-green-100">Total Amount</th>
                <th className="py-3 px-4 font-semibold border-b border-green-100">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500">
                    <Loader className="w-5 h-5 animate-spin mx-auto mb-2" />
                    Loading sales data...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-gray-500">
                    No sales found. Database is empty.
                  </td>
                </tr>
              ) : (
                filtered.map(s => (
                  <tr key={s.id} className="border-b border-green-100 hover:bg-[#F0FFF4] transition-colors">
                    <td className="py-3 px-4 font-medium text-green-900">{s.bill_number}</td>
                    <td className="py-3 px-4 text-green-700">{formatDateTime(s.date_time)}</td>
                    <td className="py-3 px-4 text-gray-700">{s.item_count} items</td>
                    <td className="py-3 px-4 font-bold text-emerald-700">Rs. {s.total_amount.toLocaleString()}</td>
                    <td className="py-3 px-4 flex gap-2">
                      <button 
                        title="View" 
                        onClick={() => handleViewSale(s)}
                        disabled={isLoadingSaleDetail}
                        className="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        <Eye className="w-4 h-4" /> View
                      </button>
                      <button 
                        title="Reprint" 
                        onClick={() => handleReprintReceipt(s)}
                        className="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                      >
                        <Printer className="w-4 h-4" /> Reprint
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* View Sale Modal */}
      <ViewSaleModal
        isOpen={viewSaleModal.open}
        onClose={() => setViewSaleModal({ open: false, sale: null })}
        sale={viewSaleModal.sale}
      />
    </div>
  );
}
