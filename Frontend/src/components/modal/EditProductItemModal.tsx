import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../ui/select';
import { Plus, Trash, DollarSign, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { categoryApi, ingredientApi, productApi } from '../../services/api';

// Mock Data
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
  onSuccess?: () => void;
  itemToEdit: {
    apiId: number;  // Real database primary key for API calls
    id: string;  // Display ID like "#PROD-1048"
    name: string;
    category_name: string;
    category_id: number;
    shelf_life: string;
    shelf_unit: string;
    cost_price: number;
    selling_price: number;
    recipe?: RecipeRow[];
    recipe_items?: Array<{
      id?: number;
      ingredientId?: string | number;
      ingredient_id?: string | number;
      qty?: string | number;
      quantity_required?: string | number;
      unit?: string;
      ingredient_unit?: string;
      ingredient_name?: string;
    }>;
  } | null;
};

const initialRecipeRow: RecipeRow = { ingredientId: '', qty: '', unit: '' };

export const EditProductItemModal: React.FC<EditProductItemModalProps> = ({ isOpen, onClose, onSuccess, itemToEdit }) => {
  const [itemId, setItemId] = useState('');
  const [apiId, setApiId] = useState(0);  // Real database primary key
  const [itemName, setItemName] = useState('');
  const [category, setCategory] = useState('');
  const [categories, setCategories] = useState<Array<{ id: number; name: string; type: string }>>([]);
  const [ingredients, setIngredients] = useState<Array<{ id: string; name: string; unit: string }>>(INGREDIENTS);
  const [isCategoriesLoading, setIsCategoriesLoading] = useState(false);
  const [shelfLife, setShelfLife] = useState('');
  const [shelfLifeUnit, setShelfLifeUnit] = useState('Days');
  const [costPrice, setCostPrice] = useState('');
  const [sellingPrice, setSellingPrice] = useState('');
  const [recipe, setRecipe] = useState<RecipeRow[]>([{ ...initialRecipeRow }]);
  const [isUpdating, setIsUpdating] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({ message: '', type: 'success', visible: false });

  // Fetch categories on component mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsCategoriesLoading(true);
        const data = await categoryApi.getProducts();
        setCategories(Array.isArray(data) ? data : data.results || []);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setCategories([]);
      } finally {
        setIsCategoriesLoading(false);
      }
    };

    fetchCategories();
  }, []);

  useEffect(() => {
    const fetchIngredients = async () => {
      try {
        const response = await ingredientApi.getAllPages();
        const mappedIngredients = (response?.items || []).map((ing: any) => ({
          id: String(ing.id),
          name: ing.name || 'Unknown',
          unit: ing.base_unit || '',
        }));

        if (mappedIngredients.length > 0) {
          setIngredients(mappedIngredients);
        }
      } catch (error) {
        console.error('Error fetching ingredients for edit modal:', error);
      }
    };

    fetchIngredients();
  }, []);

  // Pre-fill logic
  useEffect(() => {
    if (isOpen && itemToEdit) {
      setApiId(itemToEdit.apiId);  // Store real database ID
      setItemId(itemToEdit.id || '');
      setItemName(itemToEdit.name || '');
      setCategory(itemToEdit.category_id?.toString() || '');
      setShelfLife(itemToEdit.shelf_life || '');
      setShelfLifeUnit(itemToEdit.shelf_unit || 'Days');
      setCostPrice(itemToEdit.cost_price?.toString() || '');
      setSellingPrice(itemToEdit.selling_price?.toString() || '');
      const sourceRecipe =
        (Array.isArray(itemToEdit.recipe) && itemToEdit.recipe.length > 0
          ? itemToEdit.recipe
          : Array.isArray(itemToEdit.recipe_items)
          ? itemToEdit.recipe_items
          : []) || [];

      const mappedRecipe = sourceRecipe
        .map((row: any) => ({
          id: row.id,
          ingredientId: String(row.ingredientId ?? row.ingredient_id ?? ''),
          qty: row.qty ?? row.quantity_required ?? '',
          unit: row.unit ?? row.ingredient_unit ?? '',
        }))
        .filter((row: RecipeRow) => row.ingredientId || row.qty);

      setRecipe(mappedRecipe.length > 0 ? mappedRecipe : [{ ...initialRecipeRow }]);
    }
  }, [isOpen, itemToEdit]);

  // Handlers
  const handleRecipeChange = (idx: number, field: keyof RecipeRow, value: string | number) => {
    setRecipe(prev => prev.map((row, i) => {
      if (i !== idx) return row;
      if (field === 'ingredientId') {
        const found = ingredients.find(ing => ing.id === String(value));
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

  const showToast = (message: string, type: 'success' | 'error') => {
    console.log('[Toast]', { message, type });
    setToast({ message, type, visible: true });
    setTimeout(() => setToast(t => ({ ...t, visible: false })), 3000);
  };

  const handleUpdate = async () => {
    try {
      // Validation
      if (!itemId) {
        showToast('Item ID is missing', 'error');
        return;
      }

      if (!itemName.trim()) {
        showToast('Item Name is required', 'error');
        return;
      }

      if (!category) {
        showToast('Category is required', 'error');
        return;
      }

      if (!costPrice || parseFloat(costPrice as string) <= 0) {
        showToast('Cost Price must be greater than 0', 'error');
        return;
      }

      if (!sellingPrice || parseFloat(sellingPrice as string) <= 0) {
        showToast('Selling Price must be greater than 0', 'error');
        return;
      }

      setIsUpdating(true);

      // Prepare payload
      const recipeItemsPayload = recipe
        .map((row) => ({
          ingredient_id: Number(row.ingredientId),
          quantity_required: Number(row.qty),
        }))
        .filter((row) => Number.isFinite(row.ingredient_id) && row.ingredient_id > 0 && Number.isFinite(row.quantity_required) && row.quantity_required > 0);

      const payload = {
        name: itemName.trim(),
        category_id: parseInt(category, 10),
        shelf_life: shelfLife ? parseInt(shelfLife, 10) : undefined,
        shelf_unit: shelfLifeUnit,
        cost_price: parseFloat(costPrice as string),
        selling_price: parseFloat(sellingPrice as string),
        recipe_items: recipeItemsPayload,
      };

      console.log('[Update Product]', { apiId, itemId, payload });

      // Call API using real database primary key (apiId)
      await productApi.update(apiId, payload);

      showToast('✅ Product updated successfully!', 'success');

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }

      // Close modal after a short delay
      setTimeout(() => {
        onClose();
      }, 500);
    } catch (error) {
      console.error('[Update Product Error]', error);
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update product';
      showToast(`❌ ${errorMessage}`, 'error');
    } finally {
      setIsUpdating(false);
    }
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
                  <SelectValue placeholder={isCategoriesLoading ? "Loading..." : "Select Category"} />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1 min-w-[120px]">
                  {categories.map(cat => (
                    <SelectItem key={cat.id} value={cat.id.toString()} className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm">{cat.name}</SelectItem>
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
                          {ingredients.map(ing => (
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
            <Button 
              variant="outline" 
              onClick={onClose} 
              disabled={isUpdating}
              className="border-orange-300 text-orange-600 px-6 py-2 rounded-lg hover:bg-orange-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </Button>
            <Button 
              onClick={handleUpdate} 
              disabled={isUpdating}
              className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg shadow transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isUpdating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Updating...
                </>
              ) : (
                'Update Product'
              )}
            </Button>
          </div>

          {/* Toast Notification */}
          {toast.visible && (
            <div
              className={`fixed bottom-6 right-6 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 text-white z-[999] transition-all duration-300 ${
                toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'
              }`}
            >
              {toast.type === 'success' ? (
                <CheckCircle size={20} />
              ) : (
                <AlertCircle size={20} />
              )}
              <span>{toast.message}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};