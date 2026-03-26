import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui/select';
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
		category: string;
		shelfLife: string;
		shelfLifeUnit: string;
		cost: number;
		price: number;
		recipe: RecipeRow[];
	} | null;
};

const initialRecipeRow: RecipeRow = { ingredientId: '', qty: '', unit: '' };

const EditProductItemModal: React.FC<EditProductItemModalProps> = ({ isOpen, onClose, itemToEdit }) => {
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
			setCategory(itemToEdit.category || '');
			setShelfLife(itemToEdit.shelfLife || '');
			setShelfLifeUnit(itemToEdit.shelfLifeUnit || 'Days');
			setCostPrice(itemToEdit.cost?.toString() || '');
			setSellingPrice(itemToEdit.price?.toString() || '');
			setRecipe(itemToEdit.recipe || [{ ...initialRecipeRow }]);
		}
	}, [isOpen, itemToEdit]);

	// ...rest of the component implementation...

	return null;
};

export default EditProductItemModal;
