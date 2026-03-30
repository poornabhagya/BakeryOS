import { X, Search, Plus, Edit, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import EditIngredientCategoryModal from './EditIngredientCategoryModal';
import { AddIngredientCategoryModal } from './AddIngredientCategoryModal';
import DeleteConfirmationModal from '../DeleteConfirmationModal';
import { useAuth } from '../../../context/AuthContext'; // 1. Auth Import
import apiClient from '../../../services/api'; // Import API client for delete operations

interface IngredientCategory {
    id: number;
    name: string;
    type: string;
    description?: string;
}

interface IngredientCategoryListModalProps {
    isOpen: boolean;
    onClose: () => void;
    categories: IngredientCategory[];
    onCategoriesRefresh?: () => void;
}

export function IngredientCategoryListModal({ isOpen, onClose, categories = [], onCategoriesRefresh }: IngredientCategoryListModalProps) {
    const { user } = useAuth(); // 2. Get User
    // 3. Define Permissions: Only Manager & Storekeeper can Edit
    const canEdit = user?.role === 'Manager' || user?.role === 'Storekeeper';

    const [localCategories, setLocalCategories] = useState<IngredientCategory[]>(categories);
    const [searchTerm, setSearchTerm] = useState('');
    
    // Modal state for editing
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [editingCategory, setEditingCategory] = useState<IngredientCategory | null>(null);

    // Modal state for adding
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);

    // Modal state for deleting
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [deletingCategory, setDeletingCategory] = useState<IngredientCategory | null>(null);
    
    // Delete operation state
    const [isDeleting, setIsDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState<string | null>(null);
    
    // Toast notification state
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

    // Update local state when prop changes
    useEffect(() => {
        setLocalCategories(categories);
    }, [categories]);

    // Filter Logic
    const filteredCategories = localCategories.filter(cat =>
        cat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cat.id.toString().toLowerCase().includes(searchTerm.toLowerCase())
    );

    // --- HANDLERS ---

    const handleDeleteCategory = (id: number) => {
        setLocalCategories(localCategories.filter(cat => cat.id !== id));
    };

    const handleOpenEditModal = (category: IngredientCategory) => {
        setEditingCategory(category);
        setIsEditModalOpen(true);
    };

    const handleEditCategory = (data: { id: number; name: string; description?: string }) => {
        setLocalCategories(localCategories.map(cat =>
            cat.id === data.id ? { ...cat, name: data.name, description: data.description } : cat
        ));
        setIsEditModalOpen(false);
        setEditingCategory(null);
    };

    const handleAddCategory = (data: { name: string; description?: string }) => {
        if (onCategoriesRefresh) {
            onCategoriesRefresh();
        }
        setIsAddModalOpen(false);
    };

    const handleOpenDeleteModal = (category: IngredientCategory) => {
        setDeletingCategory(category);
        setIsDeleteModalOpen(true);
    };

    const handleConfirmDelete = async () => {
        if (!deletingCategory) return;
        
        setIsDeleting(true);
        setDeleteError(null);
        
        try {
            // Make API DELETE request to backend
            await apiClient.categories.delete(deletingCategory.id);
            
            // Remove from local state
            setLocalCategories(localCategories.filter(cat => cat.id !== deletingCategory.id));
            
            // Show success toast
            showToast(`Category "${deletingCategory.name}" deleted successfully!`, 'success');
            
            // Close modal and reset state
            setIsDeleteModalOpen(false);
            setDeletingCategory(null);
            
            // Trigger refresh callback to update parent component
            if (onCategoriesRefresh) {
                onCategoriesRefresh();
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to delete category';
            setDeleteError(errorMessage);
            showToast(`Error: ${errorMessage}`, 'error');
            console.error('[Delete Category Error]', err);
        } finally {
            setIsDeleting(false);
        }
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

                        {/* Table - Fixed Height Scrollable Container */}
                        <div className="h-[400px] overflow-y-scroll overflow-x-hidden border-b">
                            <table className="w-full">
                                <thead className="bg-gray-50 sticky top-0">
                                    <tr>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Category ID</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category Name</th>
                                        <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                                        {/* Hide Actions Header if not authorized */}
                                        {canEdit && <th className="py-3 px-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Actions</th>}
                                    </tr>
                                </thead>
                                <tbody className="bg-white">
                                    {filteredCategories.length > 0 ? (
                                        filteredCategories.map((category) => (
                                            <tr key={category.id} className="border-b border-gray-200 hover:bg-gray-50">
                                                <td className="px-3 py-4 text-sm font-medium text-gray-900 w-24">CAT-ING-{String(category.id).padStart(3, '0')}</td>
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
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan={canEdit ? 4 : 3} className="px-3 py-8 text-center text-gray-500">
                                                No categories found
                                            </td>
                                        </tr>
                                    )}
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
                onCategoryUpdated={onCategoriesRefresh}
            />

            <DeleteConfirmationModal
                isOpen={isDeleteModalOpen}
                onClose={() => { setIsDeleteModalOpen(false); setDeletingCategory(null); }}
                onConfirm={handleConfirmDelete}
                itemName={deletingCategory?.name || ''}
                isLoading={isDeleting}
            />
            
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
        </>
    );
}