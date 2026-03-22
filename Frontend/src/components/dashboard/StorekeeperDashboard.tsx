import { Package, Calendar, AlertTriangle, ArrowRight } from 'lucide-react';

const lowStockIngredients = [
  { name: 'All Purpose Flour', qty: '5 kg', supplier: 'Local Mills' },
  { name: 'Sugar', qty: '2 kg', supplier: 'SweetSupplies' },
  { name: 'Butter', qty: '10 packets', supplier: 'DairyCo' },
  { name: 'Yeast', qty: '500 g', supplier: 'BakePro' },
];

const expiringBatches = [
  { id: '#BAT-001', item: 'Milk', expiry: '2024-02-01', daysLeft: 2 },
  { id: '#BAT-005', item: 'Fresh Cream', expiry: '2024-02-02', daysLeft: 3 },
  { id: '#BAT-012', item: 'Bread Mix', expiry: '2024-02-05', daysLeft: 6 },
];

export function StorekeeperDashboard() {
  return (
    <div className="p-8 space-y-6">
      {/* ROW 1: METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <Package className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Low Stock Items</div>
            <div className="text-lg font-bold text-red-700">4 Items</div>
          </div>
        </div>

        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-yellow-50 border border-yellow-200">
          <div className="p-3 rounded bg-white text-yellow-600">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm text-yellow-800 font-semibold">Expiring Soon</div>
            <div className="text-lg font-bold text-yellow-700">3 Batches</div>
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
          </div>
        </div>

        {/* RIGHT: Expiring Batches */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">Expiring Batches (7 Days)</h3>
          </div>
          <div className="overflow-hidden">
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
          </div>
        </div>

      </div>
    </div>
  );
}