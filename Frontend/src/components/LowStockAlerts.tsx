import { AlertTriangle } from 'lucide-react';
import { Card } from './ui/card';

const lowStockItems = [
  { name: 'Wheat Flour', quantity: '5 kg' },
  { name: 'Sugar', quantity: '2 kg' },
];

export function LowStockAlerts() {
  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-orange-600" />
        <h3 className="text-gray-900">Low Stock Alerts</h3>
      </div>
      <div className="flex flex-wrap gap-3">
        {lowStockItems.map((item, index) => (
          <div 
            key={index} 
            className="px-4 py-3 bg-orange-50 border-l-4 border-orange-500 rounded-lg"
          >
            <p className="text-gray-900">{item.name}</p>
            <p className="text-sm text-orange-700">{item.quantity} left</p>
          </div>
        ))}
      </div>
    </Card>
  );
}