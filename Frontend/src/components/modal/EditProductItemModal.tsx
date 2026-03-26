import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/select';
import { Plus, Trash, DollarSign, Clock } from 'lucide-react';

// Mock Data
const CATEGORIES = ['Buns', 'Cakes', 'Pastries', 'Bread'];
const INGREDIENTS = [
  { id: 'i1', name: 'Flour', unit: 'kg' },
  { id: 'i2', name: 'Sugar', unit: 'kg' },
  { id: 'i3', name: 'Eggs', unit: 'pcs' },
  { id: 'i4', name: 'Butter', unit: 'g' },
];

type RecipeRow = {
  id?: number;
  ingredientId: string;
  qty: string | number;
  unit: string;
};

type EditProductItemModalProps = {
  isOpen: boolean;
  onClose: () => void;
  itemToEdit: {
    id: string;
    name: string;
    category_name: string;
    category_id: number;
    shelf_life: string;
    shelf_unit: string;
    cost_price: number;
    selling_price: number;
    recipe: RecipeRow[];
  } | null;
};

const initialRecipeRow: RecipeRow = { ingredientId: '', qty: '', unit: '' };

export const EditProductItemModal: React.FC<EditProductItemModalProps> = ({ isOpen, onClose, itemToEdit }) => {
  const [itemId, setItemId] = useState('');
  const [itemName, setItemName] = useState('');
  const [category, setCategory] = useState('');
  const [shelfLife, setShelfLife] = useState('');
  const [shelfLifeUnit, setShelfLifeUnit] = useState('Days');
  const [costPrice, setCostPrice] = useState('');
  const [sellingPrice, setSellingPrice] = useState('');
  const [recipe, setRecipe] = useState<RecipeRow[]>([{ ...initialRecipeRow }]);

  // Pre-fill logic
  useEffect(() => {
    if (isOpen && itemToEdit) {
      setItemId(itemToEdit.id || '');
      setItemName(itemToEdit.name || '');
      setCategory(itemToEdit.category_name || '');
      setShelfLife(itemToEdit.shelf_life || '');
      setShelfLifeUnit(itemToEdit.shelf_unit || 'Days');
      setCostPrice(itemToEdit.cost_price?.toString() || '');
      setSellingPrice(itemToEdit.selling_price?.toString() || '');
      setRecipe(
        itemToEdit.recipe && itemToEdit.recipe.length > 0
          ? itemToEdit.recipe.map(row => ({
              id: row.id,
              ingredientId: row.ingredientId,
              qty: row.qty,
              unit: row.unit,
            }))
          : [{ ...initialRecipeRow }]
      );
    }
  }, [isOpen, itemToEdit]);

  // Handlers
  const handleRecipeChange = (idx: number, field: keyof RecipeRow, value: string | number) => {
    setRecipe(prev => prev.map((row, i) => {
      if (i !== idx) return row;
      if (field === 'ingredientId') {
        const found = INGREDIENTS.find(ing => ing.id === value);
        return { ...row, ingredientId: value as string, unit: found ? found.unit : '', qty: '' };
      }
      return { ...row, [field]: value };
    }));
  };

  const handleAddRecipeRow = () => {
    setRecipe(prev => [...prev, { ...initialRecipeRow }]);
  };

  const handleRemoveRecipeRow = (idx: number) => {
    setRecipe(prev => prev.length === 1 ? prev : prev.filter((_, i) => i !== idx));
  };

  const handleUpdate = () => {
    // TODO: Add API logic here
    onClose();
  };

  if (!isOpen) return null;

  return (
      
      <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center overflow-y-auto">
        <div className="bg-white w-full max-w-2xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col relative overflow-hidden mx-2 border border-orange-100">
          {/* Visually hidden description for accessibility */}
          <span id="add-item-modal-desc" className="sr-only">
            Edit product details and recipe.
          </span>
          <div className="w-full p-8 sm:p-10">
            <div className="mb-8">
              <div className="flex items-center gap-4 pb-4 border-b border-orange-100">
                <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-orange-900">Edit Product Item</h2>
                <Badge className="bg-orange-500 text-white text-xs px-3 py-1 rounded-full shadow">Product</Badge>
              </div>
              {/* Close (X) button */}
              <button onClick={onClose} className="absolute top-4 right-4 p-2 rounded-lg hover:bg-orange-50 transition-colors" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          {/* ...existing code... */}

          {/* Basic Details */}
          <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6 mt-4">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Item ID</label>
              <Input value={itemId} readOnly className="bg-orange-50 border border-orange-100" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold mb-1 text-orange-700">Item Name</label>
              <Input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Fish Bun" className="border border-orange-100" />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Category</label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder="Select Category" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1 min-w-[120px]">
                  {CATEGORIES.map(cat => (
                    <SelectItem key={cat} value={cat} className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm">{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </section>

          <div className="md:col-span-4 flex flex-col sm:flex-row gap-4 items-end mb-6">
            <div className="flex-1">
              <label className="block text-xs font-semibold mb-1 text-orange-700 flex items-center gap-1"><Clock size={16} /> Shelf Life</label>
              <div className="flex gap-2">
                <Input value={shelfLife} onChange={e => setShelfLife(e.target.value)} placeholder="e.g. 2" className="w-20 border border-orange-100" />
                <Select value={shelfLifeUnit} onValueChange={setShelfLifeUnit}>
                  <SelectTrigger className="w-24 bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                    <SelectValue placeholder="Unit" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1 min-w-[90px]">
                    <SelectItem value="Days" className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm">Days</SelectItem>
                    <SelectItem value="Hours" className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm">Hours</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <hr className="my-6 border-orange-200" />

          {/* Pricing */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700 flex items-center gap-1"><DollarSign size={16} /> Cost Price</label>
              <Input value={costPrice} onChange={e => setCostPrice(e.target.value)} placeholder="e.g. 45" className="border border-orange-100" />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700 flex items-center gap-1"><DollarSign size={16} /> Selling Price</label>
              <Input value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} placeholder="e.g. 80" className="border border-orange-100" />
            </div>
            <div className="flex items-end justify-end">
              <Button
                type="button"
                variant="outline"
                className="flex items-center gap-2 text-orange-600 border-orange-300 hover:bg-orange-50"
                onClick={handleAddRecipeRow}
              >
                <Plus size={18} /> Add Ingredient
              </Button>
            </div>
          </div>

          {/* Recipe Table */}
          <div className="overflow-x-auto rounded-xl border border-orange-200 bg-orange-50 mt-6 shadow-sm">
            <table className="min-w-full text-sm">
              <thead className="bg-orange-100">
                <tr>
                  <th className="px-4 py-3 font-semibold text-left text-orange-800">Ingredient</th>
                  <th className="px-4 py-3 font-semibold text-left text-orange-800">Qty</th>
                  <th className="px-4 py-3 font-semibold text-left text-orange-800">Unit</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody>
                {recipe.map((row, idx) => (
                  <tr key={idx} className="border-b last:border-b-0 hover:bg-orange-100/60 transition-colors">
                    <td className="px-4 py-2">
                      <Select value={row.ingredientId} onValueChange={(val: string) => handleRecipeChange(idx, 'ingredientId', val)}>
                        <SelectTrigger className="w-36 bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                          <SelectValue placeholder="Select Ingredient" />
                        </SelectTrigger>
                        <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1 min-w-[120px]">
                          {INGREDIENTS.map(ing => (
                            <SelectItem key={ing.id} value={ing.id} className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm">{ing.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-4 py-2">
                      <Input value={row.qty} onChange={e => handleRecipeChange(idx, 'qty', e.target.value)} placeholder="e.g. 1" className="border-orange-200" />
                    </td>
                    <td className="px-4 py-2">
                      <Input value={row.unit} readOnly className="bg-orange-100 border-orange-200" />
                    </td>
                    <td className="px-4 py-2">
                      <Button type="button" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleRemoveRecipeRow(idx)}>
                        <Trash size={16} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 mt-6">
            <Button variant="outline" onClick={onClose} className="border-orange-300 text-orange-600 px-6 py-2 rounded-lg hover:bg-orange-100 transition-colors">Cancel</Button>
            <Button onClick={handleUpdate} className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg shadow transition-colors">Update Product</Button>
          </div>
        </div>
      </div>
    </div>
  );
};