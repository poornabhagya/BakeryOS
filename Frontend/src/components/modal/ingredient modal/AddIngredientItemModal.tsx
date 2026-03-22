import React, { useState } from 'react';
import { X, Save, Box, DollarSign, Info } from 'lucide-react';

const CATEGORIES = ['Flour', 'Dairy', 'Spices', 'Vegetables', 'Fruits', 'Oils', 'Meat', 'Seafood', 'Other'];
const SHELF_UNITS = ['Days', 'Hours'];

function generateProductId() {
	return `#PROD-${Math.floor(1000 + Math.random() * 9000)}`;
}

interface AddIngredientItemModalProps {
	open: boolean;
	onClose: () => void;
}

export function AddIngredientItemModal({ open, onClose }: AddIngredientItemModalProps) {
	const [itemId] = useState(generateProductId());
	const [itemName, setItemName] = useState('');
	const [category, setCategory] = useState('');
	const [shelfLife, setShelfLife] = useState('');
	const [shelfUnit, setShelfUnit] = useState(SHELF_UNITS[0]);
	const [costPrice, setCostPrice] = useState('');
	const [sellingPrice, setSellingPrice] = useState('');
	const [instructions, setInstructions] = useState('');
	// Preferred Supplier state
	const [preferredSupplierName, setPreferredSupplierName] = useState("");
	const [preferredSupplierContact, setPreferredSupplierContact] = useState("");
	const [trackingType, setTrackingType] = useState('weight');
	const [lowStockThreshold, setLowStockThreshold] = useState(10);

	// Profit calculation
	let profit = null;
	let profitPercent = null;
	let badgeColor = '';
	if (costPrice && sellingPrice && !isNaN(Number(costPrice)) && !isNaN(Number(sellingPrice))) {
		const cp = Number(costPrice);
		const sp = Number(sellingPrice);
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

	// ...existing code...

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
								<input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Brown Flour" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm" />
							</div>
							<div className="col-span-12 md:col-span-6">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Category</label>
								<select value={category} onChange={e => setCategory(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-sm">
									<option value="">Select Category</option>
									{CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
								</select>
							</div>
							<div className="col-span-12">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Stock Tracking Type & Unit Logic</label>
								<select value={trackingType} onChange={e => setTrackingType(e.target.value)} className="w-full px-3 py-2 border border-blue-200 rounded-lg bg-blue-50 focus:ring-2 focus:ring-blue-200 focus:border-blue-500 text-sm">
									<option value="weight">Weight (Base Unit: Grams)</option>
									<option value="volume">Volume (Base Unit: Milliliters)</option>
									<option value="count">Count (Base Unit: Numbers)</option>
								</select>
								<div className="bg-blue-50 border border-blue-200 text-blue-700 p-3 rounded-lg flex gap-2 items-start mt-2">
									<Info className="w-5 h-5 mt-0.5 text-blue-500" />
									<div className="text-sm">
										{trackingType === 'weight' && (
											<span>System tracks stock in <strong>Grams (g)</strong>. Best for solids like Flour, Sugar.</span>
										)}
										{trackingType === 'volume' && (
											<span>System tracks stock in <strong>Milliliters (ml)</strong>. Best for liquids like Oil, Milk.</span>
										)}
										{trackingType === 'count' && (
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
							<div className="col-span-12">
								<label className="block text-xs font-bold uppercase text-gray-500 mb-1">Alert when quantity drops below or equals:</label>
								<input
									type="number"
									value={lowStockThreshold}
									onChange={e => setLowStockThreshold(Number(e.target.value))}
									min={0}
									className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-sm"
								/>
							</div>
						</div>
						<div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
							<div className="text-sm text-blue-800">
								<span className="font-medium mb-2 block">Based on your setting (Qty ≤ 10):</span>
								<ul className="space-y-1">
									<li>• <strong>Out of Stock:</strong> 0 qty</li>
									<li>• <strong>Low Stock:</strong> 1 to 10 qty (Alert Triggered)</li>
									<li>• <strong>In Stock:</strong> More than 10 qty</li>
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
					<button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancel</button>
					<button type="submit" form="" className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
						<Save className="w-4 h-4" /> Save Product
					</button>
				</div>
			</div>
		</div>
	);
}

