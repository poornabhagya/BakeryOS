import React, { useState, useMemo, useEffect } from "react";
import { Search, RotateCcw, RefreshCw, Eye, Edit, Trash2, Plus, History, Loader } from "lucide-react";
import { useAuth } from '../context/AuthContext'; // 1. Auth Import එක දැම්මා
import apiClient from '../services/api';
import { convertApiProductToUi } from '../utils/conversions';

// Modals
import DeleteConfirmationModal from './modal/DeleteConfirmationModal';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { CategoryListModal } from './modal/CategoryListModal';
import { AddProductCategoryModal } from './modal/AddProductCategoryModal';
import { AddItemModal } from './modal/AddItemModal';
import { AddIngredientItemModal } from './modal/ingredient modal/AddIngredientItemModal';
import { EditProductItemModal } from './modal/EditProductItemModal';
import { ItemStockHistoryModal } from './modal/ItemStockHistoryModal';
import { ViewProductModal } from './modal/ViewProductModal';
import { IngredientStockHistoryModal } from './modal/ingredient modal/IngredientStockHistoryModal';
import { ViewIngredientDetailsModal } from './modal/ingredient modal/ViewIngredientDetailsModal';
import { AddIngredientCategoryModal } from './modal/ingredient modal/AddIngredientCategoryModal';
import { IngredientCategoryListModal } from './modal/ingredient modal/IngredientCategoryListModal';

// --- 1. Types & Mock Data ---
type Product = {
  id: string;  // product_id like "#PROD-1042"
  apiId: number;  // numeric database ID for API calls
  name: string;
  category_name: string;
  selling_price: number;
  cost_price: number;
  current_stock: number;
};

const initialProducts: Product[] = [
  { id: "#P001", apiId: 1, name: "Fish Bun", category_name: "Buns", selling_price: 80, cost_price: 45, current_stock: 8 },
  { id: "#P002", apiId: 2, name: "Tea Bun", category_name: "Buns", selling_price: 60, cost_price: 30, current_stock: 25 },
  { id: "#C001", apiId: 3, name: "Butter Cake", category_name: "Cakes", selling_price: 450, cost_price: 200, current_stock: 5 },
  { id: "#B001", apiId: 4, name: "Sandwich Bread", category_name: "Bread", selling_price: 190, cost_price: 110, current_stock: 40 },
  { id: "#D001", apiId: 5, name: "Iced Coffee", category_name: "Drinks", selling_price: 150, cost_price: 80, current_stock: 12 },
  { id: "#P003", apiId: 6, name: "Chicken Roll", category_name: "Pastry", selling_price: 120, cost_price: 60, current_stock: 0 },
];

// --- Ingredients Type & Mock Data ---
type Ingredient = {
  id: string;
  name: string;
  category: string;
  supplier: string;
  quantity: number;
  unit: string; // e.g., 'kg', 'L'
  trackingType: string;
  lowStockValue: number;
  supplierContact: string;
};

const initialIngredients: Ingredient[] = [
  { id: "#I001", name: "All-Purpose Flour", category: "Flour", supplier: "Local Mills", quantity: 50, unit: "kg", trackingType: "Weight", lowStockValue: 10, supplierContact: "071-1234567" },
  { id: "#I002", name: "Granulated Sugar", category: "Spices", supplier: "SweetSupplies", quantity: 30, unit: "kg", trackingType: "Weight", lowStockValue: 8, supplierContact: "072-2345678" },
  { id: "#I003", name: "Whole Eggs", category: "Dairy", supplier: "FarmFresh", quantity: 200, unit: "pcs", trackingType: "Count", lowStockValue: 30, supplierContact: "073-3456789" },
  { id: "#I004", name: "Butter", category: "Dairy", supplier: "DairyCo", quantity: 20, unit: "kg", trackingType: "Weight", lowStockValue: 5, supplierContact: "074-4567890" },
  { id: "#I005", name: "Cinnamon", category: "Spices", supplier: "SpiceHouse", quantity: 5, unit: "kg", trackingType: "Weight", lowStockValue: 2, supplierContact: "075-5678901" },
];

const StockManagementScreen: React.FC = () => {
  // --- Auth & Role Logic ---
  const { user } = useAuth();
  
  // Roles Defined
  const isManager = user?.role === 'Manager';
  const isCashier = user?.role === 'Cashier';
  const isBaker = user?.role === 'Baker';
  const isStorekeeper = user?.role === 'Storekeeper';

  // --- 2. States ---
  const [products, setProducts] = useState<Product[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [activeTab, setActiveTab] = useState("Products");
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isFetching, setIsFetching] = useState(true);

  // Handlers for refreshing data after adding items
  const handleProductAdded = async () => {
    try {
      const response = await apiClient.products.getAllPages();
      const uiProducts = response.items.map((uiProduct: any) => ({
        id: uiProduct.product_id,
        apiId: uiProduct.id,  // Store numeric ID for API operations
        name: uiProduct.name,
        category_name: uiProduct.category_name,
        selling_price: uiProduct.selling_price,
        cost_price: uiProduct.cost_price,
        current_stock: uiProduct.current_stock,
        shelf_life: uiProduct.shelf_life,
        shelf_unit: uiProduct.shelf_unit,
        is_active: uiProduct.is_active,
        recipe_items: uiProduct.recipe_items,
      }));
      setProducts(uiProducts);
      console.log('[StockManagementScreen] Products refreshed after new item added');
    } catch (error) {
      console.error('[StockManagementScreen] Error refreshing products:', error);
    }
  };

  const handleIngredientAdded = async () => {
    try {
      const response = await apiClient.ingredients.getAllPages();
      const uiIngredients = response.items.map((apiIngredient: any) => ({
        id: apiIngredient.ingredient_id || apiIngredient.id,
        name: apiIngredient.name,
        category: apiIngredient.category_name,
        supplier: apiIngredient.supplier || 'N/A',
        quantity: apiIngredient.total_quantity,
        unit: apiIngredient.base_unit,
        trackingType: apiIngredient.tracking_type,
        lowStockValue: apiIngredient.low_stock_threshold,
        supplierContact: apiIngredient.supplier_contact || 'N/A',
        is_active: apiIngredient.is_active,
      }));
      setIngredients(uiIngredients);
      console.log('[StockManagementScreen] Ingredients refreshed after new item added');
    } catch (error) {
      console.error('[StockManagementScreen] Error refreshing ingredients:', error);
    }
  };

  // --- Fetch Products from API (All Pages) ---
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setIsFetching(true);
        setFetchError(null);
        // Use getAllPages() to fetch all products across all pages
        const response = await apiClient.products.getAllPages();
        // response.items already contains UI-formatted products
        const uiProducts = response.items.map((uiProduct: any) => ({
          id: uiProduct.product_id,
          apiId: uiProduct.id,  // Store numeric ID for API operations
          name: uiProduct.name,
          category_name: uiProduct.category_name,
          selling_price: uiProduct.selling_price,
          cost_price: uiProduct.cost_price,
          current_stock: uiProduct.current_stock,
          shelf_life: uiProduct.shelf_life,
          shelf_unit: uiProduct.shelf_unit,
          is_active: uiProduct.is_active,
          recipe_items: uiProduct.recipe_items,
        }));
        setProducts(uiProducts);
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Failed to fetch products';
        setFetchError(errorMsg);
        console.error('Error fetching products:', error);
        // Fall back to initial mock data
        setProducts(initialProducts);
      } finally {
        setIsFetching(false);
      }
    };

    fetchProducts();
  }, []);

  // --- Fetch Ingredients from API (All Pages) ---
  useEffect(() => {
    const fetchIngredients = async () => {
      try {
        // Use getAllPages() to fetch all ingredients across all pages
        const response = await apiClient.ingredients.getAllPages();
        // Map backend API response to UI Ingredient type
        const uiIngredients = response.items.map((apiIngredient: any) => ({
          id: apiIngredient.id,  // Use numeric 'id', NOT 'ingredient_id' (which is the string like "#I013")
          name: apiIngredient.name,
          category: apiIngredient.category_name,
          supplier: apiIngredient.supplier || 'N/A',
          quantity: apiIngredient.total_quantity,
          unit: apiIngredient.base_unit,
          trackingType: apiIngredient.tracking_type,
          lowStockValue: apiIngredient.low_stock_threshold,
          supplierContact: apiIngredient.supplier_contact || 'N/A',
          is_active: apiIngredient.is_active,
        }));
        setIngredients(uiIngredients);
      } catch (error) {
        console.error('Error fetching ingredients:', error);
        // Fall back to initial mock data
        setIngredients(initialIngredients);
      }
    };

    fetchIngredients();
  }, []);

  // Logic: Storekeeper ආපු ගමන් Tab එක මාරු කරනවා Ingredients වලට
  useEffect(() => {
    if (isStorekeeper) {
      setActiveTab("Ingredients");
    }
  }, [isStorekeeper]);

  const [isIngredientCategoryListModalOpen, setIsIngredientCategoryListModalOpen] = useState(false);
  
  // Filter States
  const [searchTerm, setSearchTerm] = useState("");
  const [category, setCategory] = useState("All Categories");
  const [sortBy, setSortBy] = useState("Name A-Z");
  const [stockStatus, setStockStatus] = useState("All Items");
  const [isLoading, setIsLoading] = useState(false);
  const [isAddCategoryModalOpen, setIsAddCategoryModalOpen] = useState(false);
  const [isCategoryListModalOpen, setIsCategoryListModalOpen] = useState(false);
  const [isAddItemModalOpen, setIsAddItemModalOpen] = useState(false);
  const [isAddIngredientCategoryModalOpen, setIsAddIngredientCategoryModalOpen] = useState(false);

  // Category States
  const [productCategories, setProductCategories] = useState<{ id: number; name: string; type: string }[]>([]);
  const [ingredientCategories, setIngredientCategories] = useState<{ id: number; name: string; type: string }[]>([]);

  // Fetch Product Categories from API
  useEffect(() => {
    const fetchProductCategories = async () => {
      try {
        const response = await apiClient.categories.getProducts();
        setProductCategories(response);
      } catch (error) {
        console.error('Error fetching product categories:', error);
        // Fall back to default hardcoded categories
        setProductCategories([
          { id: 1, name: 'Buns', type: 'Product' },
          { id: 2, name: 'Cakes', type: 'Product' },
          { id: 3, name: 'Bread', type: 'Product' },
          { id: 4, name: 'Drinks', type: 'Product' },
          { id: 5, name: 'Pastry', type: 'Product' },
        ]);
      }
    };
    fetchProductCategories();
  }, []);

  // Fetch Ingredient Categories from API
  useEffect(() => {
    const fetchIngredientCategories = async () => {
      try {
        const response = await apiClient.categories.getIngredients();
        setIngredientCategories(response);
      } catch (error) {
        console.error('Error fetching ingredient categories:', error);
        // Fall back to default hardcoded categories
        setIngredientCategories([
          { id: 1, name: 'Flour', type: 'Ingredient' },
          { id: 2, name: 'Dairy', type: 'Ingredient' },
          { id: 3, name: 'Spices', type: 'Ingredient' },
        ]);
      }
    };
    fetchIngredientCategories();
  }, []);

  // Handle Category Added - Refresh the appropriate category list
  const handleCategoryAdded = async () => {
    try {
      if (activeTab === 'Products') {
        const response = await apiClient.categories.getProducts();
        setProductCategories(response);
      } else {
        const response = await apiClient.categories.getIngredients();
        setIngredientCategories(response);
      }
    } catch (error) {
      console.error('Error refreshing categories after adding new category:', error);
    }
  };
  
  // Pagination States
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 25;
  
  // Reset pagination when switching tabs
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab]);
  
  // Reset pagination when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, category, sortBy, stockStatus]);
  const [stockHistoryModal, setStockHistoryModal] = useState<{ open: boolean, itemName?: string, itemId?: string }>({ open: false });
  const [viewItem, setViewItem] = useState<{
    id: string;
    name: string;
    selling_price?: number;
    cost_price?: number;
    shelfLife?: string;
    category_name: string;
  } | null>(null);
  
  const [ingredientDetailsModal, setIngredientDetailsModal] = useState<{ open: boolean, item: any | null }>({ open: false, item: null });
  const [ingredientStockHistoryModal, setIngredientStockHistoryModal] = useState<{ open: boolean, ingredient: Ingredient | null }>({ open: false, ingredient: null });
  const [editProductModal, setEditProductModal] = useState<{ open: boolean, item: any | null }>({ open: false, item: null });
  const [deleteModal, setDeleteModal] = useState<{ open: boolean, item: Product | null }>({ open: false, item: null });
  const [isDeleting, setIsDeleting] = useState(false);

  // --- 3. Logic: Reset & Refresh ---
  const resetFilters = () => {
    setSearchTerm("");
    setCategory("All Categories");
    setSortBy("Name A-Z");
    setStockStatus("All Items");
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setProducts([...initialProducts]); 
      setIsLoading(false);
    }, 1000);
  };

  // --- 4. Logic: Filtering ---
  const filteredProducts = useMemo(() => {
    let list: any[] = activeTab === "Products" ? [...products] : [...ingredients];

    // Filter out inactive items (soft-deleted)
    list = list.filter((p) => p.is_active !== false);

    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      list = list.filter((p) => p.name.toLowerCase().includes(q) || String(p.id).toLowerCase().includes(q));
    }

    if (category !== "All Categories") {
      // Handle both products (category_name) and ingredients (category) properties
      list = list.filter((item) => {
        const itemCategory = item.category_name || item.category;
        return itemCategory === category;
      });
    }

    if (stockStatus === "Low Stock") list = list.filter((p) => p.current_stock > 0 && p.current_stock < 10);
    else if (stockStatus === "In Stock") list = list.filter((p) => p.current_stock >= 10);

    if (sortBy === "Name A-Z") list.sort((a, b) => a.name.localeCompare(b.name));
    else if (sortBy === "Name Z-A") list.sort((a, b) => b.name.localeCompare(a.name));
    else if (sortBy === "Stock Low-High") list.sort((a, b) => a.current_stock - b.current_stock);
    else if (sortBy === "Stock High-Low") list.sort((a, b) => b.current_stock - a.current_stock);

    return list;
  }, [products, ingredients, searchTerm, category, sortBy, stockStatus, activeTab]);

  // --- Pagination Logic ---
  const totalItems = filteredProducts.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedProducts = filteredProducts.slice(startIndex, endIndex);
  
  // Calculate display range for text indicator
  const displayStart = totalItems === 0 ? 0 : startIndex + 1;
  const displayEnd = Math.min(endIndex, totalItems);
  
  // Handle pagination
  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };
  
  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const exportToPDF = async () => {
    const pdf = new jsPDF();
    const table = document.querySelector('.stock-table') as HTMLElement;
    if (!table) return;

    const canvas = await html2canvas(table);
    const imgData = canvas.toDataURL('image/png');
    const imgWidth = 210; 
    const pageHeight = 295; 
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft >= 0) {
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, -heightLeft, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(`${activeTab.toLowerCase()}-stock-report.pdf`);
  };

  return (
    <div className="flex h-screen bg-[#FFF7F0]">
      {/* Main Content */}
      <div className="flex-1 flex flex-col relative overflow-hidden">
        
        {/* Top Section: Header and Tabs */}
        <div className="px-8 pt-8 pb-4 bg-white shadow-sm">
          <h2 className="text-2xl font-bold text-orange-700 mb-6">Stock Management</h2>
          <div className="flex gap-4 mb-4">
            
            {/* Products Tab: Storekeeper ට අදාළ නෑ (Hide) */}
            {!isStorekeeper && (
              <button 
                onClick={() => setActiveTab("Products")}
                className={`px-6 py-3 rounded-t-lg font-semibold border-b-4 ${activeTab === "Products" ? "text-orange-700 border-orange-500 bg-orange-50" : "text-gray-500 border-gray-200 bg-gray-50 hover:bg-gray-100"}`}
              >
                Products
              </button>
            )}

            {/* Ingredients Tab: Cashier ට අදාළ නෑ (Hide) */}
            {!isCashier && (
              <button 
                onClick={() => setActiveTab("Ingredients")}
                className={`px-6 py-3 rounded-t-lg font-semibold border-b-4 ${activeTab === "Ingredients" ? "text-orange-700 border-orange-500 bg-orange-50" : "text-gray-500 border-gray-200 bg-gray-50 hover:bg-gray-100"}`}
              >
                Ingredients
              </button>
            )}
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="px-8 py-4 bg-white flex flex-wrap gap-4 items-center border-b border-orange-100 shadow-sm z-10">
          <div className="relative">
             <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-orange-300 w-4 h-4" />
             <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search items by name or ID..."
                className="pl-10 px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 w-64 focus:outline-none focus:ring-2 focus:ring-orange-400 placeholder-orange-300"
            />
          </div>
          
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
          >
            <option>All Categories</option>
            {activeTab === "Products" ? (
              productCategories.map((cat) => (
                <option key={cat.id} value={cat.name}>{cat.name}</option>
              ))
            ) : (
              ingredientCategories.map((cat) => (
                <option key={cat.id} value={cat.name}>{cat.name}</option>
              ))
            )}
          </select>

          <select 
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 rounded-lg border border-orange-200 bg-orange-50 text-orange-900 focus:outline-none focus:ring-2 focus:ring-orange-400 cursor-pointer"
          >
            <option>Name A-Z</option>
            <option>Name Z-A</option>
            <option>Stock Low-High</option>
            <option>Stock High-Low</option>
          </select>

          <button onClick={resetFilters} className="ml-2 text-red-500 hover:text-red-700 flex items-center gap-1 font-medium text-sm">
            <RotateCcw className="w-3 h-3" /> Reset Filters
          </button>

          <button onClick={exportToPDF} className="ml-2 px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors">
            Export PDF
          </button>
        </div>

        {/* Products Data Table */}
        <div className="px-8 py-6 bg-white flex flex-col flex-1 overflow-hidden">
          <div className="flex justify-end mb-4">
            <button
              onClick={handleRefresh}
              className="p-2 rounded-full border border-orange-300 text-orange-500 hover:bg-orange-50 flex items-center gap-2 transition-colors"
              title="Refresh"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              <span className="hidden md:inline font-medium">Refresh</span>
            </button>
          </div>
          
          {/* Scrollable Table Area */}
          <div className="flex-1 overflow-y-auto bg-white border border-orange-100 rounded-lg">
            <div className="stock-table">
            {isLoading ? (
              <div className="p-12 text-center text-orange-500">Loading Stock Data...</div>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead>
                <tr className="bg-orange-50 text-orange-700">
                  <th className="py-3 px-4 font-semibold border-b border-orange-200">Item ID</th>
                  <th className="py-3 px-4 font-semibold border-b border-orange-200">Item Name</th>
                  <th className="py-3 px-4 font-semibold border-b border-orange-200">Category</th>
                  {activeTab === "Products" ? (
                    <>
                    <th className="py-3 px-4 font-semibold border-b border-orange-200">Price</th>
                    <th className="py-3 px-4 font-semibold border-b border-orange-200">Cost</th>
                    </>
                  ) : (
                    <>
                    <th className="py-3 px-4 font-semibold border-b border-orange-200">Supplier</th>
                    <th className="py-3 px-4 font-semibold border-b border-orange-200">Stock Tracking Type</th>
                    </>
                  )}
                  <th className="py-3 px-4 font-semibold border-b border-orange-200">Quantity</th>
                  <th className="py-3 px-4 font-semibold border-b border-orange-200">Actions</th>
                </tr>
                </thead>
                <tbody>
                {paginatedProducts.map((p: any) => (
                  <tr 
                    key={p.id} 
                    className={`border-b border-orange-100 transition-colors ${
                      p.is_active === false 
                        ? "bg-gray-50 opacity-60 hover:bg-gray-100" 
                        : "hover:bg-[#FFF7F0]"
                    }`}
                  >
                  <td className={`py-3 px-4 ${
                    p.is_active === false ? "text-gray-400 line-through" : "text-gray-600"
                  }`}>{p.id}</td>
                  <td className={`py-3 px-4 font-medium ${
                    p.is_active === false ? "text-gray-400" : "text-gray-800"
                  }`}>
                    {p.name}
                    {p.is_active === false && (
                      <span className="ml-2 px-2 py-1 text-xs bg-gray-300 text-gray-700 rounded font-semibold">
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className={`py-3 px-4 ${
                    p.is_active === false ? "text-gray-400" : "text-gray-600"
                  }`}>{p.category_name || p.category || 'N/A'}</td>
                  {activeTab === "Products" ? (
                    <>
                    <td className={`py-3 px-4 font-medium ${
                      p.is_active === false ? "text-gray-400" : "text-gray-800"
                    }`}>Rs. {p.selling_price}</td>
                    <td className={`py-3 px-4 ${
                      p.is_active === false ? "text-gray-400" : "text-gray-400"
                    }`}>Rs. {p.cost_price}</td>
                    </>
                  ) : (
                    <>
                    <td className={`py-3 px-4 ${
                      p.is_active === false ? "text-gray-400" : "text-gray-600"
                    }`}>{p.supplier}</td>
                    <td className={`py-3 px-4 ${
                      p.is_active === false ? "text-gray-400" : "text-gray-600"
                    }`}>{p.trackingType ? p.trackingType : <span className='italic text-gray-400'>N/A</span>}</td>
                    </>
                  )}
                  <td className="py-3 px-4">
                    {p.is_active === false ? (
                      <span className="px-2 py-1 rounded bg-gray-200 text-gray-600 font-semibold text-xs">Inactive</span>
                    ) : p.current_stock === 0 ? (
                      <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">Out of Stock</span>
                    ) : p.current_stock < 10 ? (
                      <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">{p.current_stock}{activeTab === "Ingredients" ? ` ${p.unit}` : ''}</span>
                    ) : (
                      <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">{p.current_stock}{activeTab === "Ingredients" ? ` ${p.unit}` : ''}</span>
                    )}
                  </td>
                  
                  {/* ACTIONS COLUMN - Role Based Access */}
                  <td className="py-3 px-4 flex gap-2">
                    
                    {/* Show "Inactive" message for inactive items */}
                    {p.is_active === false && (
                      <span className="text-xs text-gray-400 italic py-1">Inactive - Limited Actions</span>
                    )}
                    
                    {/* 1. View Button (Always available, including for inactive) */}
                    {p.is_active !== false && (
                      <button
                        title="View Details"
                        className="p-2 rounded hover:bg-green-100 text-green-600"
                        onClick={() => {
                          if (activeTab === "Products") {
                            setViewItem({
                              id: p.id,
                              name: p.name,
                              selling_price: p.selling_price,
                              cost_price: p.cost_price,
                              shelf_life: p.shelf_life,
                              shelf_unit: p.shelf_unit,
                              category_name: p.category_name,
                              recipe_items: p.recipe_items,
                            });
                          } else {
                            setIngredientDetailsModal({ open: true, item: p });
                          }
                        }}
                      >
                        <Eye className="w-[18px] h-[18px]" />
                      </button>
                    )}

                    {/* 2. History Button (Only for active items) */}
                    {p.is_active !== false && (
                      <button
                        title="Stock History"
                        className="p-2 rounded hover:bg-orange-100 text-orange-500"
                        onClick={() => {
                          if (activeTab === "Products") {
                            setStockHistoryModal({ open: true, itemName: p.name, itemId: p.id });
                          } else {
                            setIngredientStockHistoryModal({ open: true, ingredient: p });
                          }
                        }}
                      >
                        <History className="w-[18px] h-[18px]" />
                      </button>
                    )}

                    {/* 3. PRODUCTS EDIT/DELETE: Only Manager OR Baker (Hide for inactive) */}
                    {activeTab === "Products" && (isManager || isBaker) && p.is_active !== false && (
                      <>
                        <button
                          title="Edit"
                          className="p-2 rounded hover:bg-orange-100 text-orange-500"
                          onClick={() => {
                            setEditProductModal({ open: true, item: {
                              ...p,
                              shelfLife: "2", 
                              shelfLifeUnit: "Days", 
                              recipe: []
                            }});
                          }}
                        >
                          <Edit className="w-[18px] h-[18px]" />
                        </button>
                        <button
                          title="Delete"
                          className="p-2 rounded hover:bg-orange-100 text-red-500"
                          onClick={() => setDeleteModal({ open: true, item: p })}
                        >
                          <Trash2 className="w-[18px] h-[18px]" />
                        </button>
                      </>
                    )}

                    {/* 4. INGREDIENTS EDIT/DELETE: Only Manager OR Storekeeper (Hide for inactive) */}
                    {activeTab === "Ingredients" && (isManager || isStorekeeper) && p.is_active !== false && (
                      <>
                        <button title="Edit" className="p-2 rounded hover:bg-orange-100 text-orange-500">
                           <Edit className="w-[18px] h-[18px]" />
                        </button>
                        <button 
                          title="Delete" 
                          className="p-2 rounded hover:bg-orange-100 text-red-500"
                          onClick={() => setDeleteModal({ open: true, item: p })}
                        >
                           <Trash2 className="w-[18px] h-[18px]" />
                        </button>
                      </>
                    )}

                    {/* Delete Confirmation Modal */}
                    <DeleteConfirmationModal
                      isOpen={deleteModal.open}
                      isLoading={isDeleting}
                      onClose={() => !isDeleting && setDeleteModal({ open: false, item: null })}
                      onConfirm={async () => {
                        if (deleteModal.item) {
                          setIsDeleting(true);
                          try {
                            // Determine if deleting product or ingredient based on activeTab
                            if (activeTab === "Products") {
                              // Delete Product
                              await apiClient.products.delete(deleteModal.item.apiId);
                              // Remove from UI only if API call succeeds
                              setProducts(products => products.filter(prod => prod.id !== deleteModal.item!.id));
                              console.log(`[StockManagementScreen] Product ${deleteModal.item.name} deleted successfully`);
                            } else {
                              // Delete Ingredient - use the numeric id
                              await apiClient.ingredients.delete(deleteModal.item.id);
                              // Remove from UI only if API call succeeds
                              setIngredients(ingredients => ingredients.filter(ing => ing.id !== deleteModal.item!.id));
                              console.log(`[StockManagementScreen] Ingredient ${deleteModal.item.name} deleted successfully`);
                            }
                          } catch (error) {
                            console.error('[StockManagementScreen] Error deleting item:', error);
                            const itemType = activeTab === "Products" ? "product" : "ingredient";
                            alert(`Failed to delete ${itemType}: ${error instanceof Error ? error.message : 'Unknown error'}`);
                          } finally {
                            setIsDeleting(false);
                            setDeleteModal({ open: false, item: null });
                          }
                        }
                      }}
                      itemName={deleteModal.item?.name || ''}
                    />
                  </td>
                  </tr>
                ))}
                </tbody>
              </table>
            )}
            </div>
          </div>

          {/* Pagination Controls - Fixed Below Table */}
          <div className="flex items-center justify-between bg-white px-6 py-4 border-t border-orange-100">
            {/* Left: Showing X to Y of Z entries */}
            <div className="text-sm text-gray-600 font-medium">
              Showing {displayStart} to {displayEnd} of {totalItems} entries
            </div>
            
            {/* Right: Previous and Next Buttons */}
            <div className="flex gap-2">
              <button
                onClick={goToPreviousPage}
                disabled={currentPage === 1}
                className={`px-4 py-2 rounded-lg border font-semibold transition-colors ${
                  currentPage === 1
                    ? "border-gray-300 text-gray-400 bg-gray-50 cursor-not-allowed"
                    : "border-orange-300 text-orange-700 bg-white hover:bg-orange-50"
                }`}
              >
                Previous
              </button>
              
              <span className="px-3 py-2 text-sm font-medium text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              
              <button
                onClick={goToNextPage}
                disabled={currentPage === totalPages || totalPages === 0}
                className={`px-4 py-2 rounded-lg border font-semibold transition-colors ${
                  currentPage === totalPages || totalPages === 0
                    ? "border-gray-300 text-gray-400 bg-gray-50 cursor-not-allowed"
                    : "border-orange-300 text-orange-700 bg-white hover:bg-orange-50"
                }`}
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Footer Buttons Logic */}
        <div className="px-8 pb-6 flex justify-end items-center gap-3">
            
            {/* View Categories - හැමෝටම පේනවා */}
            {activeTab === "Products" ? (
              <button onClick={() => setIsCategoryListModalOpen(true)} className="px-4 py-2 rounded-lg border border-orange-300 text-orange-700 bg-white font-semibold hover:bg-orange-50 transition-colors">
                View Categories
              </button>
            ) : (
              <button onClick={() => setIsIngredientCategoryListModalOpen(true)} className="px-4 py-2 rounded-lg border border-blue-300 text-blue-700 bg-white font-semibold hover:bg-blue-50 transition-colors">
                View Categories
              </button>
            )}
            
            {/* Ingredient Category List Modal */}
            <IngredientCategoryListModal
              isOpen={isIngredientCategoryListModalOpen}
              onClose={() => setIsIngredientCategoryListModalOpen(false)}
              categories={ingredientCategories}
              onCategoriesRefresh={handleCategoryAdded}
            />

            {activeTab === "Products" && (isManager || isBaker) && (
              <>
                <button
                  onClick={() => setIsAddCategoryModalOpen(true)}
                  className="px-4 py-2 rounded-lg border border-orange-300 text-orange-700 bg-white font-semibold hover:bg-orange-50 transition-colors"
                >
                  Add Category
                </button>
                <button
                  className="px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors"
                  onClick={() => setIsAddItemModalOpen(true)}
                >
                  <Plus className="w-5 h-5" />
                  Add New Item
                </button>
              </>
            )}

            {/* ADD BUTTONS FOR INGREDIENTS: Manager OR Storekeeper Only */}
            {activeTab === "Ingredients" && (isManager || isStorekeeper) && (
              <>
                 <button
                  onClick={() => setIsAddIngredientCategoryModalOpen(true)}
                  className="px-4 py-2 rounded-lg border border-orange-300 text-orange-700 bg-white font-semibold hover:bg-orange-50 transition-colors"
                >
                  Add Category
                </button>
                <button
                  className="px-4 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 flex items-center gap-2 transition-colors"
                  onClick={() => setIsAddItemModalOpen(true)}
                >
                  <Plus className="w-5 h-5" />
                  Add New Item
                </button>
              </>
            )}
        </div>
      </div>
      
      {/* Modals are rendered here */}
      <AddProductCategoryModal 
        isOpen={isAddCategoryModalOpen} 
        onClose={() => setIsAddCategoryModalOpen(false)}
        onCategoryAdded={handleCategoryAdded}
      />
      <AddIngredientCategoryModal
        isOpen={isAddIngredientCategoryModalOpen}
        onClose={() => setIsAddIngredientCategoryModalOpen(false)}
        onCategoryAdded={handleCategoryAdded}
      />
      <CategoryListModal 
        isOpen={isCategoryListModalOpen} 
        onClose={() => setIsCategoryListModalOpen(false)}
        categories={productCategories}
        onCategoriesRefresh={handleCategoryAdded}
      />
      
      {activeTab === "Products" ? (
        <AddItemModal
          open={isAddItemModalOpen}
          onClose={() => setIsAddItemModalOpen(false)}
          onItemAdded={handleProductAdded}
          productCategories={productCategories}
          ingredients={ingredients.map(ing => ({
            id: Number(ing.id),  // Convert string or number ID to actual number
            name: ing.name,
            base_unit: ing.unit,
          }))}
        />
      ) : (
        <AddIngredientItemModal
          open={isAddItemModalOpen}
          onClose={() => setIsAddItemModalOpen(false)}
          onItemAdded={handleIngredientAdded}
          ingredientCategories={ingredientCategories}
        />
      )}
      
      <EditProductItemModal
        isOpen={editProductModal.open}
        onClose={() => setEditProductModal({ open: false, item: null })}
        itemToEdit={editProductModal.item}
      />
      <ItemStockHistoryModal
        open={stockHistoryModal.open && activeTab === "Products"}
        onClose={() => setStockHistoryModal({ open: false })}
        itemName={stockHistoryModal.itemName}
        itemId={stockHistoryModal.itemId}
      />
      <IngredientStockHistoryModal
        isOpen={ingredientStockHistoryModal.open && activeTab === "Ingredients"}
        onClose={() => setIngredientStockHistoryModal({ open: false, ingredient: null })}
        ingredient={ingredientStockHistoryModal.ingredient}
      />
      <ViewProductModal
        isOpen={!!viewItem && activeTab === "Products"}
        onClose={() => setViewItem(null)}
        item={viewItem as any}
      />
      <ViewIngredientDetailsModal
        isOpen={ingredientDetailsModal.open && activeTab === "Ingredients"}
        onClose={() => setIngredientDetailsModal({ open: false, item: null })}
        item={ingredientDetailsModal.item}
      />
    </div>
  );
};

export default StockManagementScreen;