import { X, Search, Plus, Edit, Trash2 } from 'lucide-react';
import { useState } from 'react';
import EditIngredientCategoryModal from './EditIngredientCategoryModal';
import { AddIngredientCategoryModal } from './AddIngredientCategoryModal';
import DeleteConfirmationModal from '../DeleteConfirmationModal'; // Path එක check කරගන්න
import { useAuth } from '../../../context/AuthContext'; // 1. Auth Import

interface IngredientCategory {
    id: string;
    name: string;
    storageType: string;
    lowStockThreshold: number;
    stockUnit: string; // e.g., kg, g, packet, L
    description?: string;
}

interface IngredientCategoryListModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const initialIngredientCategories: IngredientCategory[] = [
    { id: '#CAT-ING-001', name: 'Flour', storageType: 'Dry', lowStockThreshold: 5, stockUnit: 'kg', description: 'Basic baking ingredient' },
    { id: '#CAT-ING-002', name: 'Sugar', storageType: 'Dry', lowStockThreshold: 2, stockUnit: 'kg', description: 'Sweetener for recipes' },
    { id: '#CAT-ING-003', name: 'Milk', storageType: 'Refrigerated', lowStockThreshold: 10, stockUnit: 'Liters', description: 'Essential dairy liquid' },
    { id: '#CAT-ING-004', name: 'Butter', storageType: 'Refrigerated', lowStockThreshold: 3, stockUnit: 'Packet', description: 'Spread and cooking fat' },
];

export function IngredientCategoryListModal({ isOpen, onClose }: IngredientCategoryListModalProps) {
    const { user } = useAuth(); // 2. Get User
    // 3. Define Permissions: Only Manager & Storekeeper can Edit
    const canEdit = user?.role === 'Manager' || user?.role === 'Storekeeper';

    const [categories, setCategories] = useState<IngredientCategory[]>(initialIngredientCategories);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Modal state for editing
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingCategory, setEditingCategory] = useState<IngredientCategory | null>(null);

    // Modal state for adding
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);

    // Modal state for deleting
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [deletingCategory, setDeletingCategory] = useState<IngredientCategory | null>(null);

    // Filter Logic
    const filteredCategories = categories.filter(cat =>
        cat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cat.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // --- HANDLERS ---

    const handleDeleteCategory = (id: string) => {
        setCategories(categories.filter(cat => cat.id !== id));
    };

    const handleOpenEditModal = (category: IngredientCategory) => {
        setEditingCategory(category);
        setIsEditModalOpen(true);
    };

    const handleEditCategory = (data: { id: string; name: string; description?: string }) => {
        setCategories(categories.map(cat =>
            cat.id === data.id ? { ...cat, name: data.name, description: data.description } : cat
        ));
        setIsEditModalOpen(false);
        setEditingCategory(null);
    };

    const handleAddCategory = (data: { name: string; storageType?: string; lowStockThreshold: number; stockUnit?: string }) => {
        const newId = `#CAT-ING-${String(categories.length + 1).padStart(3, '0')}`;
        setCategories([
            ...categories,
            {
                id: newId,
                name: data.name,
                storageType: data.storageType || '',
                lowStockThreshold: data.lowStockThreshold,
                stockUnit: data.stockUnit || '',
            },
        ]);
        setIsAddModalOpen(false);
    };

    const handleOpenDeleteModal = (category: IngredientCategory) => {
        setDeletingCategory(category);
        setIsDeleteModalOpen(true);
    };

    const handleConfirmDelete = () => {
        if (deletingCategory) {
            setCategories(categories.filter(cat => cat.id !== deletingCategory.id));
        }
        setIsDeleteModalOpen(false);
        setDeletingCategory(null);
    };

    return (
        <>
            {isOpen && !isEditModalOpen && !isAddModalOpen && !isDeleteModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-white w-full max-w-md rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
                        {/* Header */}
                        <div className="flex items-center justify-between p-6 border-b border-gray-200">
                            <h3 className="text-gray-900 font-bold text-2xl">Ingredient Categories</h3>
                            <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                                <X className="w-5 h-5 text-gray-500" />
                            </button>
                        </div>

                        {/* Toolbar */}
                        <div className="p-6 bg-gray-50 border-b border-gray-200">
                            <div className="flex items-center justify-between gap-4">
                                <div className="relative flex-1 max-w-md">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                                    <input
                                        type="text"
                                        placeholder="Search categories..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                                    />
                                </div>
                                {/* 4. Add Button Logic: Only show if canEdit (Manager/Storekeeper) */}
                                {canEdit && (
                                    <button
                                        type="button"
                                        className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
                                        onClick={() => setIsAddModalOpen(true)}
                                    >
                                        <Plus className="w-4 h-4" /> Add Category
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Table */}
                        <div className="overflow-auto flex-1">
                            <table className="w-full">
                                <thead className="bg-gray-50 sticky top-0">
                                    <tr>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Category ID</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category Name</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                        {/* 5. Hide Actions Header if not authorized */}
                                        {canEdit && <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Actions</th>}
                                    </tr>
                                </thead>
                                <tbody className="bg-white">
                                    {filteredCategories.map((category) => (
                                        <tr key={category.id} className="border-b border-gray-200 hover:bg-gray-50">
                                            <td className="px-3 py-4 text-sm font-medium text-gray-900 w-24">{category.id}</td>
                                            <td className="px-3 py-4 text-sm text-gray-900">{category.name}</td>
                                            <td className="px-3 py-4 text-sm text-gray-900">{category.description || '-'}</td>
                                            {/* 6. Hide Edit/Delete Buttons if not authorized */}
                                            {canEdit && (
                                                <td className="px-3 py-4 text-sm font-medium w-16">
                                                    <div className="flex items-center gap-2">
                                                        <button
                                                            type="button"
                                                            className="p-1 text-orange-600 hover:bg-orange-50 rounded"
                                                            title="Edit"
                                                            onClick={() => handleOpenEditModal(category)}
                                                        >
                                                            <Edit className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            type="button"
                                                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                                                            onClick={() => handleOpenDeleteModal(category)}
                                                        >
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </td>
                                            )}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            <AddIngredientCategoryModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onSave={handleAddCategory}
            />
            
            <EditIngredientCategoryModal
                isOpen={isEditModalOpen}
                onClose={() => { setIsEditModalOpen(false); setEditingCategory(null); }}
                initialData={editingCategory}
                onSave={handleEditCategory}
            />

            <DeleteConfirmationModal
                isOpen={isDeleteModalOpen}
                onClose={() => { setIsDeleteModalOpen(false); setDeletingCategory(null); }}
                onConfirm={handleConfirmDelete}
                itemName={deletingCategory?.name || ''}
            />
        </>
    );
}