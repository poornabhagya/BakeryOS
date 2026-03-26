import React, { useMemo, useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Banknote, ReceiptText, TrendingUp, Eye, Printer, Search, RotateCcw, Loader } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { toNumber } from '../utils/numericUtils';
import apiClient from '../services/api';
import { convertApiSaleToUi } from '../utils/conversions';

type Sale = {
  id: number;                      // integer PK
  bill_number: string;             // "BILL-1001"
  cashier_id: number;
  cashier_name: string;
  subtotal: number;
  discount_id: number | null;
  discount_name: string | null;
  discount_amount: number;
  total_amount: number;            // Renamed from 'total'
  payment_method: string;
  item_count: number;
  date_time: string;               // ISO datetime string
  created_at: string;
};

const mockSales: Sale[] = [
  { id: 1, bill_number: 'BILL-1001', cashier_id: 1, cashier_name: 'Cashier1', subtotal: 7200, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 7000, payment_method: 'Cash', item_count: 3, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 2, bill_number: 'BILL-1002', cashier_id: 1, cashier_name: 'Cashier1', subtotal: 5100, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 5000, payment_method: 'Card', item_count: 3, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 3, bill_number: 'BILL-1003', cashier_id: 2, cashier_name: 'Cashier2', subtotal: 4100, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 4000, payment_method: 'Cash', item_count: 3, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 4, bill_number: 'BILL-1004', cashier_id: 1, cashier_name: 'Cashier1', subtotal: 3100, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 3000, payment_method: 'Cash', item_count: 4, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 5, bill_number: 'BILL-1005', cashier_id: 2, cashier_name: 'Cashier2', subtotal: 2500, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 2400, payment_method: 'Card', item_count: 3, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
  { id: 6, bill_number: 'BILL-1006', cashier_id: 1, cashier_name: 'Cashier1', subtotal: 4100, discount_id: null, discount_name: null, discount_amount: 0, total_amount: 4000, payment_method: 'Cash', item_count: 2, date_time: new Date().toISOString(), created_at: new Date().toISOString() },
];

export function SalesSummary() {
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
        // Convert API sales to UI format
        const uiSales = response.results.map(convertApiSaleToUi);
        setSales(uiSales);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch sales';
        setFetchError(errorMsg);
        console.error('Error fetching sales:', error);
        // Fall back to mock data on error
        setSales(mockSales);
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

  const filtered = useMemo(() => {
    return mockSales.filter(s => {
      const saleDate = new Date(s.date_time).toISOString().slice(0, 10);
      if (saleDate < dateFrom || saleDate > dateTo) return false;
      if (searchId.trim() && !s.bill_number.toLowerCase().includes(searchId.trim().toLowerCase())) return false;
      // Safely compare total_amount that might come as string from API
      if (amountFilter === 'High' && toNumber(s.total_amount) <= 1000) return false;
      return true;
    });
  }, [dateFrom, dateTo, searchId, amountFilter]);

  const applyTimePeriod = (period: string) => {
    const now = new Date();
    let start = new Date();
    let end = new Date();

    if (period === 'All Time') {
      start = new Date(1970,0,1);
      end = now;
    } else if (period === 'Today') {
      start = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      end = start;
    } else if (period === 'Yesterday') {
      const y = new Date(now);
      y.setDate(now.getDate() - 1);
      start = new Date(y.getFullYear(), y.getMonth(), y.getDate());
      end = start;
    } else if (period === 'This Week') {
      const day = now.getDay();
      const diff = now.getDate() - day + (day === 0 ? -6 : 1);
      start = new Date(now.setDate(diff));
      end = new Date();
    } else if (period === 'This Month') {
      start = new Date(now.getFullYear(), now.getMonth(), 1);
      end = new Date();
    }

    const toIso = (d: Date) => d.toISOString().slice(0,10);
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
    const todayIso = new Date().toISOString().slice(0,10);
    setDateFrom(todayIso);
    setDateTo(todayIso);
    setSearchId('');
    setAmountFilter('All');
  };

  const exportToPDF = async () => {
    const pdf = new jsPDF();
    const table = document.querySelector('.sales-table') as HTMLElement;
    if (!table) return;

    const canvas = await html2canvas(table);
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

    pdf.save('sales-history-report.pdf');
  };

  return (
    <div className="p-6">
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

        <div className="ml-auto flex items-center gap-3">
          <button onClick={resetFilters} className="text-red-500 hover:text-red-700 flex items-center gap-2">
            <RotateCcw className="w-4 h-4" /> Reset
          </button>

          <button onClick={exportToPDF} className="px-4 py-2 rounded-lg bg-green-500 text-white font-bold shadow hover:bg-green-600 flex items-center gap-2 transition-colors">
            Export PDF
          </button>
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
              {filtered.map(s => (
                <tr key={s.id} className="border-b border-green-100 hover:bg-[#F0FFF4] transition-colors">
                  <td className="py-3 px-4 font-medium text-green-900">{s.bill_number}</td>
                  <td className="py-3 px-4 text-green-700">{formatDateTime(s.date_time)}</td>
                  <td className="py-3 px-4 text-gray-700">{s.item_count} items</td>
                  <td className="py-3 px-4 font-bold text-emerald-700">Rs. {s.total_amount.toLocaleString()}</td>
                  <td className="py-3 px-4 flex gap-2">
                    <button title="View" className="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                      <Eye className="w-4 h-4" /> View
                    </button>
                    <button title="Reprint" className="px-3 py-1 rounded border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                      <Printer className="w-4 h-4" /> Reprint
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
