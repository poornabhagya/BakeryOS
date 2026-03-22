import { Plus } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';

interface ProductCardProps {
  id: number;
  name: string;
  price: number;
  stock: number;
  image: string;
  category: string;
  onAdd: (product: any) => void;
}

export function ProductCard({ id, name, price, stock, image, category, onAdd }: ProductCardProps) {
  const isLowStock = stock <= 5;
  const isOutOfStock = stock === 0;

  return (
    <Card 
      className={`overflow-hidden hover:shadow-lg transition-all ${
        isOutOfStock ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      }`}
      onClick={() => !isOutOfStock && onAdd({ id, name, price, stock, category })}
    >
      {/* Product Image */}
      <div className="relative h-40 bg-gray-100 overflow-hidden">
        <img 
          src={image} 
          alt={name}
          className="w-full h-full object-cover"
        />
        {/* Stock Badge */}
        <div className="absolute top-2 right-2">
          <Badge 
            className={`${
              isOutOfStock 
                ? 'bg-red-600 text-white' 
                : isLowStock 
                  ? 'bg-orange-500 text-white' 
                  : 'bg-green-600 text-white'
            }`}
          >
            {stock} Left
          </Badge>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h4 className="text-gray-900 mb-2">{name}</h4>
        <div className="flex items-center justify-between">
          <span className="text-orange-700 tabular-nums">
            Rs. {price}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              !isOutOfStock && onAdd({ id, name, price, stock, category });
            }}
            disabled={isOutOfStock}
            className={`p-2 rounded-lg transition-colors ${
              isOutOfStock
                ? 'bg-gray-200 cursor-not-allowed'
                : 'bg-orange-600 hover:bg-orange-700 text-white'
            }`}
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
      </div>
    </Card>
  );
}
