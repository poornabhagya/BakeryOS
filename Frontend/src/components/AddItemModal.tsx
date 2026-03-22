import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from './ui/dialog';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from './ui/select';
import { Plus, Trash, DollarSign, Clock } from 'lucide-react';


// Mock Data
const CATEGORIES = ['Buns', 'Cakes', 'Pastries', 'Bread'];
const INGREDIENTS = [
  { id: 'i1', name: 'Flour', unit: 'g' },
  { id: 'i2', name: 'Sugar', unit: 'g' },
  { id: 'i3', name: 'Eggs', unit: 'pcs' },
  { id: 'i4', name: 'Butter', unit: 'g' },
];

function generateProductId() {
  return `#P-${Math.floor(5000 + Math.random() * 5000)}`;
}

type RecipeRow = {
  ingredientId: string;
  quantity: string;
  unit: string;
};

type AddItemModalProps = {
  open: boolean;
  onClose: () => void;
};

const initialRecipeRow: RecipeRow = { ingredientId: '', quantity: '', unit: '' };

export const AddItemModal: React.FC<AddItemModalProps> = ({ open, onClose }) => {
  const [itemId] = useState<string>(generateProductId());
  const [itemName, setItemName] = useState<string>('');
  const [category, setCategory] = useState<string>('');
  const [shelfLife, setShelfLife] = useState<string>('');
  const [costPrice, setCostPrice] = useState<string>('');
  const [sellingPrice, setSellingPrice] = useState<string>('');
  const [recipe, setRecipe] = useState<RecipeRow[]>([{ ...initialRecipeRow }]);

  const handleRecipeChange = (idx: number, field: keyof RecipeRow, value: string) => {
    setRecipe(prev => prev.map((row, i) => {
      if (i !== idx) return row;

      // Ingredient selection change
      if (field === 'ingredientId') {
        const found = INGREDIENTS.find(ing => ing.id === value);
        let displayUnit = '';

        if (found) {
          // --- 🔥 UNIT CONVERSION LOGIC ---
          // If stock unit is kg, convert to g for recipe
          switch (found.unit) {
            case 'kg': 
              displayUnit = 'g'; 
              break;
            case 'l':  
              displayUnit = 'ml'; 
              break;
            default:   
              displayUnit = found.unit; // if pcs, g, ml, no changes
          }
        }
        return { ...row, ingredientId: value, unit: displayUnit, quantity: '' };
      }

      // Quantity change
      return { ...row, [field]: value };
    }));
  };

  const handleAddRecipeRow = () => {
    setRecipe(prev => [...prev, { ...initialRecipeRow }]);
  };

  const handleRemoveRecipeRow = (idx: number) => {
    setRecipe(prev => prev.length === 1 ? prev : prev.filter((_, i) => i !== idx));
  };

  const profitMargin =
    costPrice && sellingPrice && !isNaN(Number(costPrice)) && !isNaN(Number(sellingPrice))
      ? `${(((Number(sellingPrice) - Number(costPrice)) / Number(costPrice)) * 100).toFixed(1)}%`
      : null;

  const handleSave = () => {
    // Validation can be added here
    onClose && onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl z-[100] bg-white text-orange-900">
        <DialogDescription asChild>
          <span className="sr-only" id="add-item-modal-desc">Define a new finished product and its recipe for BakeryOS stock management.</span>
        </DialogDescription>
        <DialogHeader className="mb-2">
          <div className="flex items-center gap-3">
            <DialogTitle className="text-2xl font-bold">Add New Product Item</DialogTitle>
            <Badge className="bg-orange-500 text-white">Product</Badge>
          </div>
        </DialogHeader>
        {/* Basic Details */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Item ID</label>
            <Input value={itemId} readOnly className="bg-orange-50" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Item Name</label>
            <Input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Fish Bun" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger className="w-full bg-orange-50">
                <SelectValue placeholder="Select Category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><Clock size={16} /> Shelf Life</label>
            <Input value={shelfLife} onChange={e => setShelfLife(e.target.value)} placeholder="e.g. 2 Days" />
          </div>
        </section>
        {/* Pricing */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><DollarSign size={16} /> Cost Price (Rs.)</label>
            <Input type="number" min="0" value={costPrice} onChange={e => setCostPrice(e.target.value)} placeholder="0.00" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><DollarSign size={16} /> Selling Price (Rs.)</label>
            <Input type="number" min="0" value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} placeholder="0.00" />
          </div>
          <div className="flex items-end">
            {profitMargin && (
              <Badge className="bg-green-500 text-white">Profit Margin: {profitMargin}</Badge>
            )}
          </div>
        </section>
        {/* Recipe & Ingredients */}
        <section className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-lg">Recipe & Ingredients</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full border rounded-lg">
              <thead className="bg-orange-100">
                <tr>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Ingredient</th>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Quantity</th>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Unit</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {recipe.map((row, idx) => (
                  <tr key={idx} className="border-b last:border-b-0">
                    <td className="px-3 py-2">
                      <Select
                        value={row.ingredientId}
                        onValueChange={(val: string) => handleRecipeChange(idx, 'ingredientId', val)}
                      >
                        <SelectTrigger className="w-40 bg-orange-50">
                          <SelectValue placeholder="Select Ingredient" />
                        </SelectTrigger>
                        <SelectContent>
                          {INGREDIENTS.map(ing => (
                            <SelectItem key={ing.id} value={ing.id}>{ing.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-3 py-2">
                      <Input
                        type="number"
                        min="0"
                        value={row.quantity}
                        onChange={e => handleRecipeChange(idx, 'quantity', e.target.value)}
                        disabled={!row.ingredientId}
                        placeholder="0"
                        className="w-24"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <span className="inline-block min-w-[2.5rem]">{row.unit}</span>
                    </td>
                    <td className="px-3 py-2">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="text-red-500 hover:bg-red-100"
                        onClick={() => handleRemoveRecipeRow(idx)}
                        disabled={recipe.length === 1}
                        aria-label="Remove Ingredient"
                      >
                        <Trash size={18} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Button
            type="button"
            variant="outline"
            className="mt-3 flex items-center gap-2 text-orange-600 border-orange-300 hover:bg-orange-50"
            onClick={handleAddRecipeRow}
          >
            <Plus size={18} /> Add Ingredient Line
          </Button>
        </section>
        {/* Footer */}
        <DialogFooter className="flex flex-row gap-3 justify-end">
          <Button variant="outline" onClick={onClose} className="border-orange-300 text-orange-600">Cancel</Button>
          <Button onClick={handleSave} className="bg-orange-500 hover:bg-orange-600 text-white">Save Product</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AddItemModal;
