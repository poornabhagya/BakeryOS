import { DollarSign, AlertTriangle, TrendingUp, ShoppingCart, Star, Flame, Clock, Eye, Package, ArrowRight } from 'lucide-react';

// Mock data
const topSellingItems = [
  { name: 'Fish Bun', qty: 50, amount: 4000 },
  { name: 'Chicken Pie', qty: 35, amount: 2800 },
  { name: 'Coconut Bun', qty: 28, amount: 1960 },
  { name: 'Fish Roll', qty: 22, amount: 1760 },
  { name: 'Veg Puff', qty: 18, amount: 1080 },
];

const wastageBreakdown = [
  { reason: 'Expired', amount: 800, badgeColor: 'bg-red-100 text-red-700' },
  { reason: 'Burnt', amount: 200, badgeColor: 'bg-orange-100 text-orange-700' },
  { reason: 'Damaged', amount: 150, badgeColor: 'bg-yellow-100 text-yellow-700' },
  { reason: 'Over Prepared', amount: 100, badgeColor: 'bg-blue-100 text-blue-700' },
];

const recentTransactions = [
  { id: '#B001', time: '10:30 AM', amount: 2500 },
  { id: '#B002', time: '10:15 AM', amount: 1800 },
  { id: '#B003', time: '9:45 AM', amount: 3200 },
  { id: '#B004', time: '9:20 AM', amount: 950 },
  { id: '#B005', time: '8:55 AM', amount: 2100 },
];

const lowStockItems = [
  { name: 'Chicken Pie', qty: 5, status: 'Critical' },
  { name: 'Fish Roll', qty: 8, status: 'Low' },
  { name: 'Coconut Bun', qty: 12, status: 'Low' },
];

export function ManagerDashboard() {
  return (
    <div className="p-8 space-y-6">
      {/* ROW 1: KEY METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-green-50 border border-green-200">
          <div className="p-3 rounded bg-white text-green-600">
            <DollarSign className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-green-800 font-semibold">Total Revenue</div>
            <div className="text-lg font-bold text-green-700">Rs. 45,600</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Total Wastage Loss</div>
            <div className="text-lg font-bold text-red-700">Rs. 1,250</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-blue-50 border border-blue-200">
          <div className="p-3 rounded bg-white text-blue-600">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-blue-800 font-semibold">Net Profit</div>
            <div className="text-lg font-bold text-blue-700">Rs. 32,480</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <ShoppingCart className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Total Orders</div>
            <div className="text-lg font-bold text-orange-700">127</div>
          </div>
        </div>
      </div>

      {/* ROW 2: PERFORMANCE LISTS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">Top Selling Items (Today)</h3>
          </div>
          <div className="space-y-3">
            {topSellingItems.map((item, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <span className="text-gray-800 font-medium">{item.name}</span>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>{item.qty} pcs</span>
                  <span className="font-semibold text-gray-800">Rs. {item.amount.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Flame className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-800">Wastage Breakdown</h3>
          </div>
          <div className="space-y-3">
            {wastageBreakdown.map((item, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${item.badgeColor}`}>
                  {item.reason}
                </span>
                <span className="font-semibold text-gray-800">Rs. {item.amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ROW 3: OPERATIONAL DATA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold text-gray-800">Recent Transactions</h3>
            </div>
            <button className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1">
              View All History <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Bill ID</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Time</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Amount</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.map((transaction, index) => (
                  <tr key={index} className="border-b border-gray-100 last:border-b-0">
                    <td className="py-2 px-2 text-gray-800 font-medium">{transaction.id}</td>
                    <td className="py-2 px-2 text-gray-600">{transaction.time}</td>
                    <td className="py-2 px-2 text-gray-800 font-semibold">Rs. {transaction.amount.toLocaleString()}</td>
                    <td className="py-2 px-2">
                      <button className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1">
                        <Eye className="w-4 h-4" /> View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Package className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-semibold text-gray-800">Low Stock Alerts</h3>
            </div>
            <button className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1">
              View Inventory <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <div className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Item Name</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Remaining Qty</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {lowStockItems.map((item, index) => (
                  <tr key={index} className="border-b border-gray-100 last:border-b-0">
                    <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                    <td className="py-2 px-2 text-gray-600">{item.qty} pcs</td>
                    <td className="py-2 px-2 text-red-600 font-semibold">{item.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}