import { Flame, ChefHat, AlertCircle, Package } from 'lucide-react';

const bakeNowItems = [
  { name: 'Fish Bun', remaining: 5, target: 50, priority: 'High' },
  { name: 'Tea Bun', remaining: 12, target: 100, priority: 'Medium' },
  { name: 'Chicken Roll', remaining: 0, target: 40, priority: 'Urgent' },
];

const lowIngredients = [
  { name: 'All Purpose Flour', qty: '5 kg', status: 'Critical' },
  { name: 'Sugar', qty: '2 kg', status: 'Low' },
  { name: 'Butter', qty: '10 packets', status: 'Low' },
];

const todaysWastage = [
  { item: 'Fish Bun', qty: 5, reason: 'Burnt' },
  { item: 'Bread Dough', qty: '2 kg', reason: 'Over Fermented' },
];

export function BakerDashboard() {
  return (
    <div className="p-8 space-y-6">
      
      {/* HEADER: Production Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {/* Production Alert */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-orange-50 border border-orange-200">
          <div className="p-3 rounded bg-white text-orange-600">
            <ChefHat className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-orange-800 font-semibold">Items to Bake</div>
            <div className="text-lg font-bold text-orange-700">3 Items Critical</div>
          </div>
        </div>

        {/* Wastage Count */}
        <div className="p-4 rounded-xl shadow-sm flex items-center gap-4 bg-red-50 border border-red-200">
          <div className="p-3 rounded bg-white text-red-600">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm text-red-800 font-semibold">Today's Wastage</div>
            <div className="text-lg font-bold text-red-700">2 Issues Reported</div>
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
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Item</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Remaining</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Priority</th>
                </tr>
              </thead>
              <tbody>
                {bakeNowItems.map((item, index) => (
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
          </div>
        </div>

        {/* RIGHT: LOW INGREDIENTS */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <h3 className="text-lg font-semibold text-gray-800">Low Ingredient Alert</h3>
          </div>
          <div className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Ingredient</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Qty</th>
                  <th className="text-left py-2 px-2 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {lowIngredients.map((item, index) => (
                  <tr key={index} className="border-b border-gray-100 last:border-b-0">
                    <td className="py-2 px-2 text-gray-800 font-medium">{item.name}</td>
                    <td className="py-2 px-2 text-gray-600">{item.qty}</td>
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