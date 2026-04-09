import React, { useState } from 'react';
import { X, Save, Box, DollarSign, Info } from 'lucide-react';
import apiClient from '../../../services/api';

const CATEGORIES = ['Flour', 'Dairy', 'Spices', 'Vegetables', 'Fruits', 'Oils', 'Meat', 'Seafood', 'Other'];
// Must match Django model SHELF_UNIT_CHOICES exactly
const SHELF_UNITS = ['days', 'weeks', 'months', 'years'];
// Must match Django model TRACKING_TYPE_CHOICES exactly
const TRACKING_TYPES = ['Weight', 'Volume', 'Count'];
const THRESHOLD_UNITS: Record<string, string[]> = {
	Weight: ['kg', 'g'],
	Volume: ['L', 'ml'],
	Count: ['nos'],
};

function generateProductId() {
	return `#PROD-${Math.floor(1000 + Math.random() * 9000)}`;
}

interface AddIngredientItemModalProps {
	open: boolean;
	onClose: () => void;
	onItemAdded?: () => void; // Callback to refresh parent data
	ingredientCategories: { id: number; name: string; type: string }[];
}

export function AddIngredientItemModal({ open, onClose, onItemAdded, ingredientCategories }: AddIngredientItemModalProps) {
	const [itemId] = useState(generateProductId());
	const [itemName, setItemName] = useState('');
	const [category, setCategory] = useState('');
	const [shelfLife, setShelfLife] = useState('');
	const [shelfUnit, setShelfUnit] = useState('days'); // Must match Django choices
	const [instructions, setInstructions] = useState('');
	// Preferred Supplier state
	const [preferredSupplierName, setPreferredSupplierName] = useState("");
	const [preferredSupplierContact, setPreferredSupplierContact] = useState("");
	const [trackingType, setTrackingType] = useState('Weight'); // Must match Django choices
	const [lowStockThreshold, setLowStockThreshold] = useState(10);
	const [thresholdUnit, setThresholdUnit] = useState('kg');
	
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
				console.error('[AddIngredientItemModal] Backend validation errors:', details);
				return errorMessages.join(' | ');
			}
		}
		
		// Fallback to error message
		if (err instanceof Error) {
			return err.message;
		}
		
		return 'Failed to create ingredient';
	};

	// Profit calculation not needed for ingredients
	const badgeColor = '';

	// ...existing code...

	React.useEffect(() => {
		const allowedUnits = THRESHOLD_UNITS[trackingType] || ['g'];
		if (!allowedUnits.includes(thresholdUnit)) {
			setThresholdUnit(allowedUnits[0]);
		}
	}, [trackingType, thresholdUnit]);

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsLoading(true);
		setError(null);
		
		try {
			// Validate required fields
			if (!itemName.trim()) {
				throw new Error('Item name is required');
			}
			if (!category) {
				throw new Error('Category is required');
			}
			
			// Parse numeric fields to ensure correct types
			const lowStockNum = parseFloat(String(lowStockThreshold));
			const shelfLifeNum = shelfLife ? parseFloat(shelfLife) : 30;
			
			if (isNaN(lowStockNum)) {
				throw new Error('Low stock threshold must be a valid number');
			}
			if (isNaN(shelfLifeNum)) {
				throw new Error('Shelf life must be a valid number');
			}
			
			// Determine canonical base_unit based on tracking_type
			// Weight -> g, Volume -> ml, Count -> nos
			let baseUnit = 'g';
			if (trackingType === 'Volume') {
				baseUnit = 'ml';
			} else if (trackingType === 'Count') {
				baseUnit = 'nos';
			}
			
			// Construct payload matching Django Ingredient serializer EXACTLY
			const payload = {
				name: itemName.trim(),
				category_id: Number(category), // PrimaryKey - must be integer ID
				tracking_type: trackingType, // Must be 'Weight', 'Volume', or 'Count' (capitalized!)
				base_unit: baseUnit, // Required: 'kg', 'liters', or 'pieces'
				low_stock_threshold: lowStockNum, // User raw threshold value
				threshold_unit: thresholdUnit,
				shelf_life: shelfLifeNum, // Integer field
				shelf_unit: shelfUnit, // Already lowercase from state: 'days', 'weeks', 'months', 'years'
				supplier: preferredSupplierName?.trim() || null,
				supplier_contact: preferredSupplierContact?.trim() || null,
			};
			
			console.log('[AddIngredientItemModal] Creating ingredient with payload:', payload);
			
			// Make API call to create ingredient
			const createdIngredient = await apiClient.ingredients.create(payload);
			
			// Show success toast
			showToast(`Ingredient "${itemName}" created successfully!`, 'success');
			console.log('[AddIngredientItemModal] Ingredient created:', createdIngredient);
			
			// Reset form
			setItemName('');
			setCategory('');
			setInstructions('');
			setPreferredSupplierName('');
			setPreferredSupplierContact('');
			setThresholdUnit('kg');
			
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
			console.error('[AddIngredientItemModal] Error creating ingredient:', err);
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
						<h3 className="text-lg font-bold text-gray-900 tracking-tight">Add New Ingredient Item</h3>
					</div>
					<button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-50 transition-colors">
						<X className="w-5 h-5 text-gray-400" />
					</button>
				</div>

				{/* Scrollable Body */}
				<form id="addIngredientForm" className="flex-1 overflow-y-auto p-6 min-h-0" style={{ maxHeight: 'calc(90vh - 120px)' }} onSubmit={handleSave}>
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
								<input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Brown Flour" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
							</div>
							<div className="col-span-12 md:col-span-6">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Category</label>
								<select value={category} onChange={e => setCategory(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm">
									<option value="">Select Category</option>
								{ingredientCategories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
								</select>
							</div>
							<div className="col-span-12">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Stock Tracking Type & Unit Logic</label>
								<select value={trackingType} onChange={e => setTrackingType(e.target.value)} className="w-full px-3 py-2 border border-blue-200 rounded-lg bg-blue-50 focus:ring-2 focus:ring-blue-200 focus:border-blue-500 text-sm">
							{TRACKING_TYPES.map(type => (
								<option key={type} value={type}>
									{type === 'Weight' && 'Weight (Base Unit: Grams)'}
									{type === 'Volume' && 'Volume (Base Unit: Milliliters)'}
									{type === 'Count' && 'Count (Base Unit: Numbers)'}
								</option>
							))}
								</select>
								<div className="bg-blue-50 border border-blue-200 text-blue-700 p-3 rounded-lg flex gap-2 items-start mt-2">
									<Info className="w-5 h-5 mt-0.5 text-blue-500" />
									<div className="text-sm">
										{trackingType === 'Weight' && (
											<span>System tracks stock in <strong>Grams (g)</strong>. Best for solids like Flour, Sugar.</span>
										)}
										{trackingType === 'Volume' && (
											<span>System tracks stock in <strong>Milliliters (ml)</strong>. Best for liquids like Oil, Milk.</span>
										)}
										{trackingType === 'Count' && (
											<span>System tracks stock by <strong>Count (nos)</strong>. Best for Eggs, Packets.</span>
										)}
									</div>
								</div>
							</div>
						</div>
					</div>

					{/* Stock Status Thresholds Section */}
					<div className="mb-6 bg-orange-50 rounded-xl border border-orange-100 p-4">
						<div className="flex items-center gap-2 mb-4">
							<DollarSign className="w-4 h-4 text-orange-400" />
							<span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Stock Status Thresholds</span>
						</div>
						<p className="text-sm text-gray-600 mb-4">Define when items in this category should be marked as Low Stock.</p>
						<div className="grid grid-cols-12 gap-4 items-end">
							<div className="col-span-12 md:col-span-8">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Alert when quantity drops below or equals:</label>
								<input
									type="number"
									value={lowStockThreshold}
									onChange={e => setLowStockThreshold(Number(e.target.value))}
									min={0}
									className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-sm"
								/>
							</div>
							<div className="col-span-12 md:col-span-4">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Threshold Unit</label>
								<select
									value={thresholdUnit}
									onChange={e => setThresholdUnit(e.target.value)}
									className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-sm"
								>
									{(THRESHOLD_UNITS[trackingType] || ['g']).map(unit => (
										<option key={unit} value={unit}>{unit}</option>
									))}
								</select>
							</div>
						</div>
						<div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
							<div className="text-sm text-blue-800">
								<span className="font-medium mb-2 block">Based on your setting (Qty ≤ {lowStockThreshold} {thresholdUnit}):</span>
								<ul className="space-y-1">
									<li>• <strong>Out of Stock:</strong> 0 qty</li>
									<li>• <strong>Low Stock:</strong> Qty less than or equal to your threshold</li>
									<li>• <strong>In Stock:</strong> Qty greater than your threshold</li>
								</ul>
							</div>
						</div>
					</div>

					{/* Preferred Supplier Section */}
					<div className="mb-6 bg-white rounded-xl border border-gray-100 p-4">
						<div className="flex items-center gap-2 mb-2">
							<span className="text-xs font-bold uppercase text-gray-500 tracking-wider">Preferred Supplier</span>
						</div>
						<div className="grid grid-cols-12 gap-4">
							<div className="col-span-12 md:col-span-6">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Supplier Name</label>
								<input
									type="text"
									value={preferredSupplierName}
									onChange={e => setPreferredSupplierName(e.target.value)}
									placeholder="Enter supplier name"
									className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm"
								/>
							</div>
							<div className="col-span-12 md:col-span-6">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Contact Number</label>
								<input
									type="text"
									value={preferredSupplierContact}
									onChange={e => setPreferredSupplierContact(e.target.value)}
									placeholder="Enter contact number"
									className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm"
								/>
							</div>
						</div>
					</div>
				</form>

				{/* Sticky Footer */}
				<div className="sticky bottom-0 z-10 bg-white border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
					<button type="button" onClick={onClose} disabled={isLoading} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">Cancel</button>
					<button type="submit" form="addIngredientForm" disabled={isLoading} className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
						{isLoading ? (
							<>
								<span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
								Saving...
							</>
						) : (
							<>
								<Save className="w-4 h-4" /> Save Ingredient
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

