import { X, Search, Plus, Edit, Trash2 } from 'lucide-react';
import { useState } from 'react';
import EditCategoryModal from './EditCategoryModal';
import { AddProductCategoryModal } from './AddProductCategoryModal';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import { useAuth } from '../../context/AuthContext'; // 1. Import Auth Context

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

export function CategoryListModal({ isOpen, onClose }: CategoryListModalProps) {
    const { user } = useAuth(); // 2. Get User
    const isCashier = user?.role === 'Cashier'; // 3. Check if Cashier

    const [categories, setCategories] = useState<Category[]>(initialCategories);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Modal states
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingCategory, setEditingCategory] = useState<Category | null>(null);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
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

    const handleOpenEditModal = (category: Category) => {
        setEditingCategory(category);
        setIsEditModalOpen(true);
    };

    const handleEditCategory = (data: { id: string; name: string; lowStockThreshold: number }) => {
        setCategories(categories.map(cat =>
            cat.id === data.id ? { ...cat, name: data.name, lowStockThreshold: data.lowStockThreshold } : cat
        ));
        setIsEditModalOpen(false);
        setEditingCategory(null);
    };

    const handleAddCategory = (data: { name: string; lowStockThreshold: number }) => {
        const newId = `#CAT-${String(categories.length + 1).padStart(3, '0')}`;
        setCategories([...categories, { id: newId, ...data }]);
        setIsAddModalOpen(false);
    };

    const handleOpenDeleteModal = (category: Category) => {
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
                            <h3 className="text-gray-900 font-bold text-2xl">Product Categories</h3>
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
                                {/* 4. Hide ADD Button for Cashier */}
                                {!isCashier && (
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
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">ID</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-auto">Category Name</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-28">Low Stock</th>
                                        {/* Hide Actions Header for Cashier */}
                                        {!isCashier && <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Actions</th>}
                                    </tr>
                                </thead>
                                <tbody className="bg-white">
                                    {filteredCategories.map((category) => (
                                        <tr key={category.id} className="border-b border-gray-200 hover:bg-gray-50">
                                            <td className="px-3 py-4 text-sm font-medium text-gray-900 w-16">{category.id}</td>
                                            <td className="px-3 py-4 text-sm text-gray-900 w-auto">{category.name}</td>
                                            <td className="px-3 py-4 text-sm text-gray-900 w-28">
                                                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                                                    ≤ {category.lowStockThreshold} qty
                                                </span>
                                            </td>
                                            {/* 5. Hide Edit/Delete Buttons for Cashier */}
                                            {!isCashier && (
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

            <AddProductCategoryModal
                isOpen={isAddModalOpen}
                onClose={() => setIsAddModalOpen(false)}
                onSave={handleAddCategory}
            />

            <EditCategoryModal
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