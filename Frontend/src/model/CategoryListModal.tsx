import { X, Search, Plus, Edit, Trash2 } from 'lucide-react';
import { useState } from 'react';
import EditCategoryModal from './EditCategoryModal';
import AddProductCategoryModal from './AddProductCategoryModal';
import DeleteConfirmationModal from './DeleteConfirmationModal';

interface Category {
	id: string;
	name: string;
	lowStockThreshold: number;
}

interface CategoryListModalProps {
	isOpen: boolean;
	onClose: () => void;
}

const initialCategories: Category[] = [
	{ id: '#CAT-001', name: 'Buns', lowStockThreshold: 10 },
	{ id: '#CAT-002', name: 'Cakes', lowStockThreshold: 5 },
	{ id: '#CAT-003', name: 'Pastries', lowStockThreshold: 8 },
	{ id: '#CAT-004', name: 'Bread', lowStockThreshold: 12 },
];

const CategoryListModal = ({ isOpen, onClose }: CategoryListModalProps) => {
	const [categories, setCategories] = useState<Category[]>(initialCategories);
	const [searchTerm, setSearchTerm] = useState('');
    
	// Modal state for editing
	const [isEditModalOpen, setIsEditModalOpen] = useState(false);
	const [editingCategory, setEditingCategory] = useState<Category | null>(null);

	// Modal state for adding
	const [isAddModalOpen, setIsAddModalOpen] = useState(false);

	// Modal state for deleting
	const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
	const [deletingCategory, setDeletingCategory] = useState<Category | null>(null);

	// Filter Logic
	const filteredCategories = categories.filter(cat =>
		cat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
		cat.id.toLowerCase().includes(searchTerm.toLowerCase())
	);

	// --- HANDLERS ---

	const handleDeleteCategory = (id: string) => {
		setCategories(categories.filter(cat => cat.id !== id));
	};

	// Handler to open edit modal
	const handleOpenEditModal = (category: Category) => {
		setEditingCategory(category);
		setIsEditModalOpen(true);
	};

	// Handler to save edits
	const handleEditCategory = (data: { id: string; name: string; lowStockThreshold: number }) => {
		setCategories(categories.map(cat =>
			cat.id === data.id ? { ...cat, ...data } : cat
		));
		setIsEditModalOpen(false);
	};

	// Handler to open add modal
	const handleOpenAddModal = () => {
		setIsAddModalOpen(true);
	};

	// Handler to add new category
	const handleAddCategory = (data: { name: string; lowStockThreshold: number }) => {
		const newCategory: Category = {
			id: `#CAT-${Math.floor(1000 + Math.random() * 9000)}`,
			name: data.name,
			lowStockThreshold: data.lowStockThreshold,
		};
		setCategories([...categories, newCategory]);
		setIsAddModalOpen(false);
	};

	// Handler to open delete modal
	const handleOpenDeleteModal = (category: Category) => {
		setDeletingCategory(category);
		setIsDeleteModalOpen(true);
	};

	// Handler to confirm delete
	const handleConfirmDelete = () => {
		if (deletingCategory) {
			handleDeleteCategory(deletingCategory.id);
			setIsDeleteModalOpen(false);
		}
	};

	if (!isOpen) return null;

	return (
		<div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
			<div className="absolute inset-0" aria-hidden="true" onClick={onClose}></div>
			<div className="relative z-10 w-full max-w-2xl mx-auto p-0" style={{ pointerEvents: 'auto' }}>
				<div className="animate-fade-in-scale bg-white rounded-2xl shadow-xl border border-orange-100 px-8 py-8 min-w-[400px]">
					<div className="flex items-center justify-between mb-6">
						<h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Product Categories</h2>
						<button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close">
							<X className="w-6 h-6 text-gray-400" />
						</button>
					</div>
					<div className="flex items-center gap-3 mb-6">
						<div className="relative flex-1">
							<input
								type="text"
								placeholder="Search categories..."
								value={searchTerm}
								onChange={e => setSearchTerm(e.target.value)}
								className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-200 text-gray-700"
							/>
							<Search className="absolute right-3 top-2.5 w-5 h-5 text-gray-400" />
						</div>
						<button
							onClick={handleOpenAddModal}
							className="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-300"
						>
							<Plus className="w-5 h-5" /> Add Category
						</button>
					</div>
					<div className="overflow-x-auto">
						<table className="min-w-full divide-y divide-gray-200">
							<thead>
								<tr>
									<th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
									<th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Name</th>
									<th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Low Stock Threshold</th>
									<th className="px-4 py-2"></th>
								</tr>
							</thead>
							<tbody className="bg-white divide-y divide-gray-100">
								{filteredCategories.map(category => (
									<tr key={category.id}>
										<td className="px-4 py-2 text-sm text-gray-700 font-mono">{category.id}</td>
										<td className="px-4 py-2 text-sm text-gray-900 font-semibold">{category.name}</td>
										<td className="px-4 py-2 text-sm text-gray-700">{category.lowStockThreshold}</td>
										<td className="px-4 py-2 flex gap-2">
											<button
												onClick={() => handleOpenEditModal(category)}
												className="p-2 rounded-lg hover:bg-orange-100 transition-colors"
												aria-label="Edit"
											>
												<Edit className="w-5 h-5 text-orange-500" />
											</button>
											<button
												onClick={() => handleOpenDeleteModal(category)}
												className="p-2 rounded-lg hover:bg-red-100 transition-colors"
												aria-label="Delete"
											>
												<Trash2 className="w-5 h-5 text-red-500" />
											</button>
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				</div>
			</div>
			{/* Modals */}
			{isEditModalOpen && editingCategory && (
				<EditCategoryModal
					isOpen={isEditModalOpen}
					onClose={() => setIsEditModalOpen(false)}
					category={editingCategory}
					onSave={handleEditCategory}
				/>
			)}
			{isAddModalOpen && (
				<AddProductCategoryModal
					isOpen={isAddModalOpen}
					onClose={() => setIsAddModalOpen(false)}
					onAdd={handleAddCategory}
				/>
			)}
			{isDeleteModalOpen && deletingCategory && (
				<DeleteConfirmationModal
					isOpen={isDeleteModalOpen}
					onClose={() => setIsDeleteModalOpen(false)}
					onConfirm={handleConfirmDelete}
					itemName={deletingCategory.name}
				/>
			)}
		</div>
	);
};

export default CategoryListModal;
