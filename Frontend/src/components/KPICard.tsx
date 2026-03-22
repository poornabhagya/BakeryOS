import { LucideIcon } from 'lucide-react';
import { Card } from './ui/card';

interface KPICardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  valueColor?: string;
  badge?: number;
}

export function KPICard({ 
  title, 
  value, 
  icon: Icon, 
  valueColor = 'text-gray-900',
  badge
}: KPICardProps) {
  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-2">{title}</p>
          <h2 className={`${valueColor} tabular-nums`}>{value}</h2>
        </div>
        <div className="relative">
          <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
            <Icon className="w-6 h-6 text-orange-600" />
          </div>
          {badge !== undefined && (
            <div className="absolute -top-2 -right-2 bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">
              {badge}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}