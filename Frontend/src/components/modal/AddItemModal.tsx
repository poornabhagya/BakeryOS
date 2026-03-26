
import React, { useState } from 'react';
import { toNumber } from '../../utils/numericUtils';

interface RecipeRow {
	ingredientId: string;
	quantity: string;
	unit: string;
}

interface AddItemModalProps {
	open: boolean;
	onClose: () => void;
}
import { X, Plus, Trash2, Save, Box, DollarSign, Calculator } from 'lucide-react';

const CATEGORIES = ['Buns', 'Cakes', 'Pastries', 'Bread', 'Drinks'];
const INGREDIENTS = [
	{ id: 'i1', name: 'Flour', unit: 'kg' },
	{ id: 'i2', name: 'Sugar', unit: 'kg' },
	{ id: 'i3', name: 'Butter', unit: 'g' },
	{ id: 'i4', name: 'Eggs', unit: 'nos' },
	{ id: 'i5', name: 'Yeast', unit: 'g' },
];
const SHELF_UNITS = ['Days', 'Hours'];

function generateProductId() {
	return `#PROD-${Math.floor(1000 + Math.random() * 9000)}`;
}

export function AddItemModal({ open, onClose }: AddItemModalProps) {
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
    setRecipeRows(prev => prev.map((row, i) => {
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
		setRecipeRows(prev => [...prev, { ingredientId: '', quantity: '', unit: '' }]);
	};

	const handleRemoveRecipeRow = (idx: number) => {
		setRecipeRows(prev => prev.length === 1 ? prev : prev.filter((_, i) => i !== idx));
	};

	const handleSave = () => {
		onClose && onClose();
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
				<form className="flex-1 overflow-y-auto p-6 min-h-0" style={{ maxHeight: 'calc(90vh - 120px)' }} onSubmit={e => { e.preventDefault(); handleSave(); }}>
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
									{CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
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
													{INGREDIENTS.map(ing => (
														<option key={ing.id} value={ing.id}>{ing.name}</option>
													))}
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
					<button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancel</button>
					<button type="submit" form="" className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
						<Save className="w-4 h-4" /> Save Product
					</button>
				</div>
			</div>
		</div>
	);
}
