



import React, { useState } from 'react';
import { X, Plus, Trash2, Save, Box, DollarSign, Calculator } from 'lucide-react';

const CATEGORIES = ['Buns', 'Cakes', 'Pastries', 'Bread', 'Drinks'];
const INGREDIENTS = [
	{ id: 'i1', name: 'Flour', unit: 'kg' },
	{ id: 'i2', name: 'Sugar', unit: 'kg' },
	{ id: 'i3', name: 'Butter', unit: 'g' },
	{ id: 'i4', name: 'Eggs', unit: 'pcs' },
	{ id: 'i5', name: 'Yeast', unit: 'g' },
];
const SHELF_UNITS = ['Days', 'Hours'];

function generateProductId() {
	return `#PROD-${Math.floor(1000 + Math.random() * 9000)}`;
}

import type { FC } from 'react';
const AddItemModal: FC<{ open: boolean; onClose: () => void }> = ({ open, onClose }) => {
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

	const handleRecipeChange = (idx, field, value) => {
		setRecipeRows(prev => prev.map((row, i) => {
			if (i !== idx) return row;
			if (field === 'ingredientId') {
				const found = INGREDIENTS.find(ing => ing.id === value);
				return { ...row, ingredientId: value, unit: found ? found.unit : '', quantity: '' };
			}
			return { ...row, [field]: value };
		}));
	};

	// ...rest of the component implementation...
	return null; // TODO: Implement modal UI
	}

	export { AddItemModal };
	export default AddItemModal;
