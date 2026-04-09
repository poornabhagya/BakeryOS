import React, { useState, useEffect } from 'react';
import { Button } from '../../ui/button';
import { Input } from '../../ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../../ui/select';
import { CheckCircle, AlertCircle } from 'lucide-react';
import apiClient, { ingredientApi } from '../../../services/api';

const THRESHOLD_UNITS: Record<string, string[]> = {
  Weight: ['kg', 'g'],
  Volume: ['L', 'ml'],
  Count: ['nos'],
};

type EditIngredientItemModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  ingredient: {
    apiId: number;  // Real database primary key for API calls
    id: string;  // Display ID like "#I001"
    name: string;
    category: string;  // Category name for display
    categoryId: number;  // Numeric category ID for API calls
    supplier: string;
    quantity: number;
    unit: string;
    trackingType: string;
    lowStockValue: number;
    thresholdUnit?: string;
    supplierContact: string;
    shelfLife?: number;  // Duration number for shelf life
    shelfUnit?: string;  // Unit for shelf life: days, weeks, months, years
  } | null;
};

const TRACKING_TYPES = ['Weight', 'Volume', 'Count'];
const UNIT_OPTIONS = ['kg', 'g', 'L', 'ml', 'pcs', 'ltr', 'cup'];

type CategoryOption = {
  id: number;
  name: string;
  type: string;
};

export const EditIngredientItemModal: React.FC<EditIngredientItemModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  ingredient,
}) => {
  // State for form fields
  const [ingredientId, setIngredientId] = useState('');
  const [apiId, setApiId] = useState(0);  // Real database primary key
  const [ingredientName, setIngredientName] = useState('');
  const [category, setCategory] = useState('');  // Category name for display
  const [categoryId, setCategoryId] = useState(0);  // Numeric category ID for API calls
  const [supplier, setSupplier] = useState('');
  const [quantity, setQuantity] = useState('');
  const [unit, setUnit] = useState('kg');
  const [trackingType, setTrackingType] = useState('Weight');
  const [lowStockValue, setLowStockValue] = useState('');
  const [supplierContact, setSupplierContact] = useState('');
  const [shelfLife, setShelfLife] = useState('30');
  const [shelfUnit, setShelfUnit] = useState('days');
  const [thresholdUnit, setThresholdUnit] = useState('kg');

  // Categories state
  const [categories, setCategories] = useState<CategoryOption[]>([]);
  const [isCategoriesLoading, setIsCategoriesLoading] = useState(false);

  // Loading and notification states
  const [isUpdating, setIsUpdating] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean }>({
    message: '',
    type: 'success',
    visible: false,
  });

  // Pre-fill form when ingredient changes
  useEffect(() => {
    if (isOpen && ingredient) {
      setApiId(ingredient.apiId);  // Store real database ID
      setIngredientId(ingredient.id || '');
      setIngredientName(ingredient.name || '');
      setCategory(ingredient.category || '');  // Display name
      setCategoryId(ingredient.categoryId || 0);  // Numeric ID for API
      setSupplier(ingredient.supplier || '');
      setQuantity(ingredient.quantity?.toString() || '');
      setUnit(ingredient.unit || 'kg');
      setTrackingType(ingredient.trackingType || 'Weight');
      setLowStockValue(ingredient.lowStockValue?.toString() || '');
      setSupplierContact(ingredient.supplierContact || '');
      // Use defaults for shelf_life and shelf_unit if not available
      setShelfLife(ingredient.shelfLife?.toString() || '30');
      setShelfUnit(ingredient.shelfUnit || 'days');
      setThresholdUnit(ingredient.thresholdUnit || 'kg');
    }
  }, [isOpen, ingredient]);

  useEffect(() => {
    const allowedUnits = THRESHOLD_UNITS[trackingType] || ['g'];
    if (!allowedUnits.includes(thresholdUnit)) {
      setThresholdUnit(allowedUnits[0]);
    }
  }, [trackingType, thresholdUnit]);

  // Fetch ingredient categories from API
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsCategoriesLoading(true);
        const fetchedCategories = await apiClient.categories.getIngredients();
        setCategories(fetchedCategories);
        console.log('[EditIngredientItemModal] Fetched categories:', fetchedCategories);
      } catch (error) {
        console.error('[EditIngredientItemModal] Error fetching categories:', error);
        // Continue gracefully - categories just won't be pre-fetched
        setCategories([]);
      } finally {
        setIsCategoriesLoading(false);
      }
    };

    if (isOpen) {
      fetchCategories();
    }
  }, [isOpen]);

  // Toast helper
  const showToast = (message: string, type: 'success' | 'error') => {
    console.log('[Toast]', { message, type });
    setToast({ message, type, visible: true });
    setTimeout(() => setToast(t => ({ ...t, visible: false })), 3000);
  };

  // Handle update submission
  const handleUpdate = async () => {
    try {
      // Validation - Check all required fields
      if (!ingredientName.trim()) {
        showToast('Ingredient Name is required', 'error');
        return;
      }

      if (!category) {
        showToast('Category is required', 'error');
        return;
      }

      if (!supplier.trim()) {
        showToast('Supplier is required', 'error');
        return;
      }

      if (!quantity || parseFloat(quantity as string) < 0) {
        showToast('Quantity must be a valid number >= 0', 'error');
        return;
      }

      if (!unit) {
        showToast('Unit is required', 'error');
        return;
      }

      if (!trackingType) {
        showToast('Tracking Type is required', 'error');
        return;
      }

      if (!lowStockValue || parseFloat(lowStockValue as string) < 0) {
        showToast('Low Stock Value must be a valid number >= 0', 'error');
        return;
      }

      if (!shelfLife || parseInt(shelfLife) <= 0) {
        showToast('Shelf Life must be greater than 0', 'error');
        return;
      }

      if (!shelfUnit) {
        showToast('Shelf Unit is required', 'error');
        return;
      }

      setIsUpdating(true);

      // Prepare payload - Send all fields the backend IngredientUpdateSerializer accepts
      // Backend accepts: name, category_id, tracking_type, total_quantity, supplier, supplier_contact, 
      //                   base_unit, low_stock_threshold, shelf_life, shelf_unit, is_active
      const payload = {
        name: ingredientName.trim(),  // Ingredient name
        category_id: parseInt(categoryId.toString(), 10),  // Strict parsing with radix 10 - numeric category ID only
        tracking_type: trackingType,  // Weight, Volume, or Count
        total_quantity: parseFloat(quantity as string),  // Current stock quantity
        supplier: supplier.trim(),  // Supplier name
        supplier_contact: supplierContact.trim(),  // Supplier contact info
        base_unit: unit,  // Unit: kg, g, L, ml, etc.
        low_stock_threshold: parseFloat(lowStockValue as string),  // Low stock alert threshold
        threshold_unit: thresholdUnit,
        shelf_life: parseInt(shelfLife, 10),  // Strict parsing with radix 10
        shelf_unit: shelfUnit,  // Shelf life unit: days, weeks, months, years
      };

      console.log('[Update Ingredient]', { apiId, ingredientId, payload });

      // Call API using real database primary key (apiId)
      await ingredientApi.update(apiId, payload);

      showToast('✅ Ingredient updated successfully!', 'success');

      // Call onSuccess callback if provided
      if (onSuccess) {
        onSuccess();
      }

      // Close modal after a short delay
      setTimeout(() => {
        onClose();
      }, 500);
    } catch (error) {
      console.error('[Update Ingredient Error]', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to update ingredient';
      showToast(`❌ ${errorMessage}`, 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center overflow-y-auto">
      <div className="bg-white w-full max-w-2xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col relative overflow-hidden mx-2 border border-orange-100">
        {/* Header */}
        <div className="w-full p-8 sm:p-10">
          <div className="mb-8">
            <div className="flex items-center gap-4 pb-4 border-b border-orange-100">
              <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-orange-900">
                Edit Ingredient
              </h2>
            </div>
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-2 rounded-lg hover:bg-orange-50 transition-colors"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>

          {/* Basic Details */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Ingredient ID</label>
              <Input value={ingredientId} readOnly className="bg-orange-50 border border-orange-100" />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Ingredient Name *</label>
              <Input
                value={ingredientName}
                onChange={e => setIngredientName(e.target.value)}
                placeholder="e.g. All-Purpose Flour"
                className="border border-orange-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Category *</label>
              <Select 
                value={categoryId.toString()} 
                onValueChange={(value: string) => {
                  const selectedCategory = categories.find(cat => cat.id === parseInt(value, 10));
                  setCategoryId(parseInt(value, 10));
                  setCategory(selectedCategory?.name || '');
                }}
              >
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder={isCategoriesLoading ? 'Loading categories...' : 'Select a category'} />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1">
                  {categories.map(cat => (
                    <SelectItem
                      key={cat.id}
                      value={cat.id.toString()}
                      className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm"
                    >
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {categoryId > 0 && (
                <span className="text-xs text-gray-500 mt-1 block">Category ID: {categoryId}</span>
              )}
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Supplier *</label>
              <Input
                value={supplier}
                onChange={e => setSupplier(e.target.value)}
                placeholder="e.g. Local Mills"
                className="border border-orange-100"
              />
            </div>
          </section>

          <hr className="my-6 border-orange-200" />

          {/* Stock Details */}
          <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Quantity *</label>
              <Input
                type="number"
                value={quantity}
                onChange={e => setQuantity(e.target.value)}
                placeholder="e.g. 50"
                className="border border-orange-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Unit *</label>
              <Select value={unit} onValueChange={setUnit}>
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder="Select Unit" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1">
                  {UNIT_OPTIONS.map(u => (
                    <SelectItem
                      key={u}
                      value={u}
                      className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm"
                    >
                      {u}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Low Stock Value *</label>
              <Input
                type="number"
                value={lowStockValue}
                onChange={e => setLowStockValue(e.target.value)}
                placeholder="e.g. 10"
                className="border border-orange-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Threshold Unit *</label>
              <Select value={thresholdUnit} onValueChange={setThresholdUnit}>
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder="Select Unit" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1">
                  {(THRESHOLD_UNITS[trackingType] || ['g']).map(u => (
                    <SelectItem
                      key={u}
                      value={u}
                      className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm"
                    >
                      {u}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </section>

          {/* Tracking and Contact */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Tracking Type *</label>
              <Select value={trackingType} onValueChange={setTrackingType}>
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder="Select Tracking Type" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1">
                  {TRACKING_TYPES.map(t => (
                    <SelectItem
                      key={t}
                      value={t}
                      className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm"
                    >
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Supplier Contact</label>
              <Input
                value={supplierContact}
                onChange={e => setSupplierContact(e.target.value)}
                placeholder="e.g. 071-1234567"
                className="border border-orange-100"
              />
            </div>
          </section>

          <hr className="my-6 border-orange-200" />

          {/* Shelf Life Details */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Shelf Life Duration *</label>
              <Input
                type="number"
                value={shelfLife}
                onChange={e => setShelfLife(e.target.value)}
                placeholder="e.g. 30"
                className="border border-orange-100"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1 text-orange-700">Shelf Life Unit *</label>
              <Select value={shelfUnit} onValueChange={setShelfUnit}>
                <SelectTrigger className="w-full bg-white border border-orange-200 rounded-md shadow-sm focus:ring-2 focus:ring-orange-200 focus:border-orange-400 transition-all text-orange-900 text-sm py-2 px-3 min-h-[36px]">
                  <SelectValue placeholder="Select Unit" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-orange-200 rounded-md shadow-lg mt-1 py-1">
                  {['days', 'weeks', 'months', 'years'].map(unit => (
                    <SelectItem
                      key={unit}
                      value={unit}
                      className="px-3 py-1.5 hover:bg-orange-100 focus:bg-orange-200 text-orange-900 cursor-pointer rounded-md transition-all text-sm"
                    >
                      {unit.charAt(0).toUpperCase() + unit.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </section>

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
                'Save Changes'
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
