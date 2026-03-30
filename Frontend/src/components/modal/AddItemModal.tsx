
import React, { useState, useEffect } from 'react';
import { toNumber } from '../../utils/numericUtils';
import apiClient from '../../services/api';

interface RecipeRow {
	ingredientId: string;
	quantity: string;
	unit: string;
}

interface AddItemModalProps {
	open: boolean;
	onClose: () => void;
	onItemAdded?: () => void; // Callback to refresh parent data
	productCategories: { id: number; name: string; type: string }[];
	ingredients: { id: number; name: string; base_unit: string }[]; // Real database ingredients
}
import { X, Plus, Trash2, Save, Box, DollarSign, Calculator } from 'lucide-react';

const SHELF_UNITS = ['days', 'weeks', 'months', 'years'];

function generateProductId() {
	return `#PROD-${Math.floor(1000 + Math.random() * 9000)}`;
}

export function AddItemModal({ open, onClose, onItemAdded, productCategories, ingredients }: AddItemModalProps) {
	// Log that the component received ingredients
	useEffect(() => {
		if (open && ingredients && ingredients.length > 0) {
			console.log('[AddItemModal] Received ingredients prop:', ingredients);
		} else if (open) {
			console.warn('[AddItemModal] WARNING - No ingredients prop or empty array!');
		}
	}, [open, ingredients]);
	
	const [itemId] = useState(generateProductId());
	const [itemName, setItemName] = useState('');
	const [category, setCategory] = useState('');
	const [shelfLife, setShelfLife] = useState('');
	const [shelfUnit, setShelfUnit] = useState(SHELF_UNITS[0]);
	const [costPrice, setCostPrice] = useState('');
	const [sellingPrice, setSellingPrice] = useState('');
	const [instructions, setInstructions] = useState('');
	const [recipeRows, setRecipeRows] = useState([
		{ ingredientId: '', quantity: '', unit: '' },
	]);
	
	// Loading and toast states
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [toast, setToast] = useState<{ message: string; type: 'success' | 'error'; visible: boolean; key: number }>({
	  message: '',
	  type: 'success',
	  visible: false,
	  key: 0,
	});
	
	// Toast helper function
	const showToast = (message: string, type: 'success' | 'error') => {
	  setToast(prev => ({ message, type, visible: true, key: prev.key + 1 }));
	  setTimeout(() => setToast(t => ({ ...t, visible: false })), 3000);
	};

	// Helper to parse validation errors from API responses
	const parseValidationErrors = (err: any): string => {
		// Check if this is an ApiError with details object
		if (err?.details && typeof err.details === 'object') {
			const details = err.details;
			const errorMessages: string[] = [];
			
			// Parse field-specific errors
			for (const [field, messages] of Object.entries(details)) {
				if (Array.isArray(messages)) {
					errorMessages.push(`${field}: ${messages.join(', ')}`);
				} else if (typeof messages === 'string') {
					errorMessages.push(`${field}: ${messages}`);
				}
			}
			
			if (errorMessages.length > 0) {
				console.error('[AddItemModal] Backend validation errors:', details);
				return errorMessages.join(' | ');
			}
		}
		
		// Fallback to error message
		if (err instanceof Error) {
			return err.message;
		}
		
		return 'Failed to create product';
	};

	// Profit calculation
	let profit = null;
	let profitPercent = null;
	let badgeColor = '';
	if (costPrice && sellingPrice && !isNaN(toNumber(costPrice)) && !isNaN(toNumber(sellingPrice))) {
		const cp = toNumber(costPrice);
		const sp = toNumber(sellingPrice);
		if (sp > cp) {
			profit = sp - cp;
			profitPercent = ((profit / cp) * 100).toFixed(1);
			badgeColor = 'bg-green-100 text-green-700 border-green-300';
		} else if (sp < cp) {
			profit = cp - sp;
			profitPercent = ((profit / cp) * 100).toFixed(1);
			badgeColor = 'bg-red-100 text-red-700 border-red-300';
		}
	}

	const handleRecipeChange = (idx: number, field: keyof RecipeRow, value: string) => {
    console.log(`[AddItemModal] handleRecipeChange - idx: ${idx}, field: ${field}, value: "${value}"`);
    
    setRecipeRows(prev => {
      const updated = prev.map((row, i) => {
        if (i !== idx) return row;

        // Ingredient selection change
        if (field === 'ingredientId') {
          const found = ingredients.find(ing => ing.id.toString() === value);
          let displayUnit = '';

          if (found) {
            // Use the ingredient's base_unit from the database
            displayUnit = found.base_unit || '';
            console.log(`[AddItemModal] Ingredient selected: id=${found.id}, name=${found.name}, unit=${displayUnit}`);
          } else {
            console.warn(`[AddItemModal] Ingredient not found for value: "${value}"`);
          }
          const newRow = { ...row, ingredientId: value, unit: displayUnit, quantity: '' };
          console.log(`[AddItemModal] Updated row ${idx}:`, newRow);
          return newRow;
        }

        // Quantity change
        const newRow = { ...row, [field]: value };
        console.log(`[AddItemModal] Updated row ${idx} (${field}):`, newRow);
        return newRow;
      });
      
      console.log(`[AddItemModal] New recipeRows state after change:`, updated);
      return updated;
    });
  };

	const handleAddRecipeRow = () => {
		setRecipeRows(prev => [...prev, { ingredientId: '', quantity: '', unit: '' }]);
	};

	const handleRemoveRecipeRow = (idx: number) => {
		setRecipeRows(prev => prev.length === 1 ? prev : prev.filter((_, i) => i !== idx));
	};

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);
		
		try {
			console.log('[AddItemModal] ===== FORM SUBMISSION START =====');
			console.log('[AddItemModal] Current recipeRows state:', recipeRows);
			
			// Validate required fields
			if (!itemName.trim()) {
				throw new Error('Item name is required');
			}
			if (!category) {
				throw new Error('Category is required');
			}
			if (!costPrice || !sellingPrice) {
				throw new Error('Cost and selling prices are required');
			}
			
			console.log('[AddItemModal] Basic field validation passed');
			
			// Parse numeric fields to ensure correct types
			const costPriceNum = parseFloat(costPrice);
			const sellingPriceNum = parseFloat(sellingPrice);
			
			if (isNaN(costPriceNum) || isNaN(sellingPriceNum)) {
				throw new Error('Cost and selling prices must be valid numbers');
			}
			
			console.log('[AddItemModal] Price parsing passed:', { costPriceNum, sellingPriceNum });
			
			// Build recipe items array - filter out empty rows
			console.log('[AddItemModal] Before filtering - recipeRows:', recipeRows);
			
			const filteredRows = recipeRows.filter(row => {
				const hasIngredient = row.ingredientId && row.ingredientId.trim() !== '';
				const hasQuantity = row.quantity && row.quantity.trim() !== '';
				console.log(`[AddItemModal] Row filtering - ingredientId: "${row.ingredientId}" (has: ${hasIngredient}), quantity: "${row.quantity}" (has: ${hasQuantity})`);
				return hasIngredient && hasQuantity;
			});
			
			console.log('[AddItemModal] After filtering - filteredRows count:', filteredRows.length);
			console.log('[AddItemModal] Filtered rows data:', filteredRows);
			
			const recipeItems = filteredRows.map((row, idx) => {
				const ingredientId = Number(row.ingredientId);
				const quantityRequired = parseFloat(row.quantity);
				console.log(`[AddItemModal] Mapping row ${idx}: ingredientId=${ingredientId} (from "${row.ingredientId}"), quantity=${quantityRequired} (from "${row.quantity}")`);
				
				if (isNaN(ingredientId)) {
					console.warn(`[AddItemModal] WARNING - ingredientId is NaN for row ${idx}`);
				}
				if (isNaN(quantityRequired)) {
					console.warn(`[AddItemModal] WARNING - quantityRequired is NaN for row ${idx}`);
				}
				
				return {
					ingredient_id: ingredientId,
					quantity_required: quantityRequired,
				};
			});
			
			console.log('[AddItemModal] Final recipeItems array:', recipeItems);
			console.log('[AddItemModal] recipeItems count:', recipeItems.length);
			
			// Construct payload matching Django Product model
			const payload = {
				name: itemName.trim(),
				category_id: Number(category),
				cost_price: costPriceNum,
				selling_price: sellingPriceNum,
				shelf_life: shelfLife ? Number(shelfLife) : null,
				shelf_unit: shelfUnit.toLowerCase(),
				preparation_instructions: instructions.trim() || null,
				current_stock: 0,
				recipe_items: recipeItems, // MUST BE INCLUDED
			};
			
			console.log('[AddItemModal] ===== FINAL PAYLOAD =====');
			console.log('[AddItemModal] Submitting payload:', JSON.stringify(payload, null, 2));
			console.log('[AddItemModal] Payload has recipe_items:', !!payload.recipe_items);
			console.log('[AddItemModal] recipe_items is array:', Array.isArray(payload.recipe_items));
			console.log('[AddItemModal] recipe_items length:', payload.recipe_items?.length);
			
			// Make API call to create product
			const createdProduct = await apiClient.products.create(payload as any);
			
			console.log('[AddItemModal] ===== API RESPONSE =====');
			console.log('[AddItemModal] Product created successfully:', createdProduct);
			
			// Show success toast
			showToast(`Product "${itemName}" created successfully!`, 'success');
			
			// Reset form
			setItemName('');
			setCategory('');
			setCostPrice('');
			setSellingPrice('');
			setInstructions('');
			setRecipeRows([{ ingredientId: '', quantity: '', unit: '' }]);
			
			// Close modal after short delay to show toast
			setTimeout(() => {
				onClose();
				// Trigger parent refresh callback
				if (onItemAdded) {
					onItemAdded();
				}
			}, 1000);
			
		} catch (err) {
			const errorMessage = parseValidationErrors(err);
			setError(errorMessage);
			showToast(`Error: ${errorMessage}`, 'error');
			console.error('[AddItemModal] ===== ERROR =====');
			console.error('[AddItemModal] Error creating product:', err);
		} finally {
			setIsLoading(false);
		}
	};

	if (!open) return null;

	return (
		<div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center overflow-y-auto">
			<div className="bg-white w-full max-w-4xl max-h-[90vh] rounded-xl shadow-2xl flex flex-col relative overflow-hidden mx-2">
				{/* Sticky Header */}
				<div className="sticky top-0 z-10 bg-white border-b border-gray-200 flex items-center justify-between px-6 py-4">
					<div className="flex items-center gap-2">
						<Box className="w-5 h-5 text-orange-500" />
						<h3 className="text-lg font-bold text-gray-900 tracking-tight">Add New Product Item</h3>
					</div>
					<button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-50 transition-colors">
						<X className="w-5 h-5 text-gray-400" />
					</button>
				</div>

				{/* Scrollable Body */}
				<form id="addItemForm" className="flex-1 overflow-y-auto p-6 min-h-0" style={{ maxHeight: 'calc(90vh - 120px)' }} onSubmit={handleSave}>
					{/* Basic Info Section */}
					<div className="mb-6 bg-white rounded-xl border border-gray-100 p-4">
						<div className="flex items-center gap-2 mb-4">
							<Box className="w-4 h-4 text-orange-400" />
							<span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Basic Info</span>
						</div>
						<div className="grid grid-cols-12 gap-4">
							<div className="col-span-12 md:col-span-3">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Item ID</label>
								<input value={itemId} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-gray-400 cursor-not-allowed text-sm" />
							</div>
							<div className="col-span-12 md:col-span-9">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Item Name</label>
								<input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Fish Bun" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
							</div>
							<div className="col-span-12 md:col-span-6">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Category</label>
								<select value={category} onChange={e => setCategory(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm">
									<option value="">Select Category</option>
								{productCategories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
								</select>
							</div>
							<div className="col-span-12 md:col-span-6 flex gap-2">
								<div className="flex-1">
									<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Shelf Life</label>
									<input value={shelfLife} onChange={e => setShelfLife(e.target.value)} placeholder="e.g. 2" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
								</div>
								<div>
									<label className="block text-xs font-bold uppercase text-gray-500 mb-1">&nbsp;</label>
									<select value={shelfUnit} onChange={e => setShelfUnit(e.target.value)} className="w-full px-2 py-2 border border-gray-200 rounded-lg bg-gray-100 focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm">
										{SHELF_UNITS.map(u => <option key={u} value={u}>{u}</option>)}
									</select>
								</div>
							</div>
						</div>
					</div>

					{/* Pricing Section */}
					<div className="mb-6 bg-orange-50 rounded-xl border border-orange-100 p-4">
						<div className="flex items-center gap-2 mb-4">
							<DollarSign className="w-4 h-4 text-orange-400" />
							<span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Pricing & Profit</span>
						</div>
						<div className="grid grid-cols-12 gap-4 items-end">
							<div className="col-span-12 md:col-span-4">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Cost Price (Rs.)</label>
								<input type="number" min="0" value={costPrice} onChange={e => setCostPrice(e.target.value)} placeholder="e.g. 50" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
							</div>
							<div className="col-span-12 md:col-span-4">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Selling Price (Rs.)</label>
								<input type="number" min="0" value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} placeholder="e.g. 80" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
							</div>
							<div className="col-span-12 md:col-span-4 flex items-center h-full">
								{profit !== null && sellingPrice && costPrice && (
									<span className={`inline-block px-3 py-1 rounded-full border text-xs font-semibold ${badgeColor}`}>
										{Number(sellingPrice) > Number(costPrice)
											? `Profit: Rs. ${profit} (${profitPercent}%)`
											: Number(sellingPrice) < Number(costPrice)
											? `Loss: Rs. ${profit} (${profitPercent}%)`
											: 'No Profit'}
									</span>
								)}
							</div>
						</div>
						<div className="mt-6">
							<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Preparation Instructions</label>
							<textarea value={instructions} onChange={e => setInstructions(e.target.value)} placeholder="e.g. Bake at 180C for 20 mins" className="w-full px-3 py-2 border border-gray-200 rounded-lg min-h-[40px] resize-none focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
						</div>
					</div>

					{/* Recipe Ingredients Section */}
					<div className="mb-6 bg-white rounded-xl border border-gray-100 p-4">
						<div className="flex items-center justify-between mb-2">
							<div className="flex items-center gap-2">
								<Calculator className="w-4 h-4 text-orange-400" />
								<span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Recipe Ingredients</span>
							</div>
							<button type="button" onClick={handleAddRecipeRow} className="flex items-center gap-1 text-orange-600 hover:underline text-xs font-semibold px-2 py-1 rounded transition-colors">
								<Plus className="w-4 h-4" /> Add Ingredient
							</button>
						</div>
						<div className="overflow-x-auto max-h-60 overflow-y-auto rounded-lg border border-gray-100 min-h-[48px]">
							<table className="min-w-full text-sm">
								<thead className="sticky top-0 bg-gray-50 z-10">
									<tr>
										<th className="px-3 py-2 text-left text-xs font-bold uppercase text-gray-500">Ingredient</th>
										<th className="px-3 py-2 text-left text-xs font-bold uppercase text-gray-500">Quantity</th>
										<th className="px-3 py-2 text-left text-xs font-bold uppercase text-gray-500">Unit</th>
										<th className="px-3 py-2"></th>
									</tr>
								</thead>
								<tbody>
									{recipeRows.map((row, idx) => (
										<tr key={idx} className="border-b last:border-b-0 hover:bg-orange-50">
											<td className="px-3 py-1">
												<select
													value={row.ingredientId}
													onChange={e => handleRecipeChange(idx, 'ingredientId', e.target.value)}
													className="w-40 px-2 py-1 border border-gray-200 rounded-lg bg-gray-100 focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
												>
													<option value="">Select Ingredient</option>
													{ingredients.length > 0 ? (
														ingredients.map(ing => (
															<option key={ing.id} value={ing.id}>{ing.name}</option>
														))
													) : (
														<option disabled>No ingredients available</option>
													)}
												</select>
											</td>
											<td className="px-3 py-1">
												<input
													type="number"
													min="0"
													value={row.quantity}
													onChange={e => handleRecipeChange(idx, 'quantity', e.target.value)}
													disabled={!row.ingredientId}
													placeholder="0"
													className="w-24 px-2 py-1 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
												/>
											</td>
											<td className="px-3 py-1">
												<span className="inline-block min-w-[2.5rem] text-gray-700">
													{row.unit}
												</span>
											</td>
											<td className="px-3 py-1">
												<button
													type="button"
													className="p-2 rounded-full hover:bg-orange-100 text-red-500"
													onClick={() => handleRemoveRecipeRow(idx)}
													disabled={recipeRows.length === 1}
													aria-label="Remove Ingredient"
												>
													<Trash2 className="w-4 h-4" />
												</button>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					</div>
				</form>

				{/* Sticky Footer */}
				<div className="sticky bottom-0 z-10 bg-white border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
				<button type="button" onClick={onClose} disabled={isLoading} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">Cancel</button>
				<button type="submit" form="addItemForm" disabled={isLoading} className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
					{isLoading ? (
						<>
							<span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
							Saving...
						</>
					) : (
						<>
							<Save className="w-4 h-4" /> Save Product
						</>
					)}
				</button>
			</div>
			
			{/* Toast Notification */}
			{toast.visible && (
			  <div
			    key={toast.key}
			    className={`fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg text-white font-medium z-50 animate-fade-in ${
			      toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'
			    }`}
			  >
			    {toast.message}
			  </div>
			)}
			</div>
		</div>
	);
}
