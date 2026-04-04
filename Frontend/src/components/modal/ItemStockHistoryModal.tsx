import React, { useState, useEffect } from 'react';
import { X, ArrowLeft, Plus, Search } from 'lucide-react';
import { AddNewBatchModal } from './AddNewBatchModal';
import { AddProductWastageModal } from '../modal/AddProductWastageModal';
import { useAuth } from '../../context/AuthContext'; // 1. Import Auth Context
import apiClient from '../../services/api';

interface Batch {
  id?: number;  // Numeric database ID
  batchId: string;
  madeDate: string;
  expireDate: string;
  quantity: number;
  currentQty?: number;
  status: string;
  notes?: string;
}

interface ItemStockHistoryModalProps {
  open: boolean;
  onClose: () => void;
  itemName?: string;
  itemId?: string;
  productApiId?: number;  // Actual database primary key
  onStockUpdated?: () => void | Promise<void>;
}

export const ItemStockHistoryModal: React.FC<ItemStockHistoryModalProps> = ({ open, onClose, itemName, itemId, productApiId, onStockUpdated }) => {
  const { user } = useAuth(); // 2. Get User
  const isCashier = user?.role === 'Cashier'; // 3. Check Role

  const [view, setView] = useState<'list' | 'add'>('list');
  const [batches, setBatches] = useState<Batch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addBatchModalOpen, setAddBatchModalOpen] = useState(false);
  const [wastageModalOpen, setWastageModalOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<any>(null);
  const [search, setSearch] = useState('');
  const [productUnitCost, setProductUnitCost] = useState<number | string>(0);

  // Fetch product details to get unit cost
  useEffect(() => {
    if (!open || !productApiId) {
      setProductUnitCost(0);
      return;
    }

    const fetchProductUnitCost = async () => {
      try {
        const productResponse = await apiClient.products.getById(productApiId);
        if (productResponse?.cost_price) {
          setProductUnitCost(productResponse.cost_price);
        }
      } catch (err) {
        console.error('[ItemStockHistoryModal] Error fetching product:', err);
        setProductUnitCost(0);
      }
    };

    fetchProductUnitCost();
  }, [open, productApiId]);

  const fetchBatches = async () => {
    if (!open || !productApiId) {
      setBatches([]);
      setError(null);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      if (!productApiId || isNaN(productApiId)) {
        console.warn('[ItemStockHistoryModal] Invalid product API ID:', productApiId);
        setError('Invalid product ID');
        return;
      }

      console.log('[ItemStockHistoryModal] Fetching batches for product API ID:', productApiId, 'from itemName:', itemName);
      const response = await apiClient.batches.getProductBatchesById(productApiId);
      console.log('[ItemStockHistoryModal] API Response:', response);

      const batchesArray = Array.isArray(response)
        ? response
        : ((response as any)?.results || (response as any)?.data || []);

      const mappedBatches: Batch[] = (batchesArray || []).map((batch: any) => {
        const currentQtyFromApi = batch.current_qty !== undefined ? batch.current_qty : batch.currentQty;
        const qty = parseFloat(batch.quantity) || 0;
        const curQty = currentQtyFromApi !== undefined ? parseFloat(currentQtyFromApi) : qty;

        return {
          id: batch.id,
          batchId: String(batch.batch_id || batch.id || `BATCH-${Date.now()}`),
          madeDate: String(batch.made_date) ? `${batch.made_date}T00:00` : new Date().toISOString(),
          expireDate: String(batch.expire_date) ? `${batch.expire_date}T00:00` : new Date().toISOString(),
          quantity: qty,
          currentQty: !isNaN(curQty) ? curQty : qty,
          status: String(batch.status || 'Active'),
          notes: String(batch.notes || ''),
        };
      });

      setBatches(mappedBatches);
    } catch (err) {
      console.error('[ItemStockHistoryModal] Error fetching batches:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch batches');
      setBatches([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, [open, productApiId, itemName]);

  const handleBatchCreated = async () => {
    await fetchBatches();
    if (onStockUpdated) {
      await onStockUpdated();
    }
  };

  const filteredBatches = batches.filter(batch =>
        (batch.batchId?.toLowerCase() || '').includes(search.toLowerCase()) ||
        (batch.madeDate?.toLowerCase() || '').includes(search.toLowerCase()) ||
        (batch.expireDate?.toLowerCase() || '').includes(search.toLowerCase()) ||
        (batch.notes?.toLowerCase() || '').includes(search.toLowerCase())
      );

      function getQtyLabel(qty: number) {
        if (qty === 0) return 'bg-red-100 text-red-700 px-2 py-1 rounded font-bold';
        if (qty < 10) return 'bg-red-100 text-red-700 px-2 py-1 rounded font-bold';
        return 'bg-green-100 text-green-700 px-2 py-1 rounded font-bold';
      }

      if (!open) return null;

      return (
        <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-8">
          <div className="bg-white w-full max-w-lg h-[85vh] rounded-xl shadow-2xl flex flex-col relative overflow-hidden overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 z-10 bg-white border-b border-gray-200 flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-2">
                {view === 'add' && (
                  <button
                    onClick={() => setView('list')}
                    className="p-2 rounded-lg hover:bg-orange-50 transition-colors"
                    aria-label="Back to list"
                  >
                    <ArrowLeft className="w-5 h-5 text-orange-500" />
                  </button>
                )}
                <h3 className="text-lg font-bold text-gray-900 tracking-tight">
                  {view === 'add' ? 'Add New Batch' : (productApiId ? 'Production History' : 'Stock Batches')}
                </h3>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-orange-50 transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            {/* Item Info */}
            <div className="px-6 pt-2 pb-2 border-b border-gray-100 flex items-center gap-4 bg-white">
              <span className="font-semibold text-orange-600">{itemName}</span>
              <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                {itemId}
              </span>
            </div>
            {/* Body */}
            <div className="flex-1 overflow-y-auto p-6 min-h-0">
              {view === 'list' ? (
                <>
                  {/* Toolbar */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="relative w-full max-w-xs">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <input
                        type="text"
                        placeholder="Search batches..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
                      />
                    </div>
                    {/* 4. Hide ADD NEW STOCK button for Cashier */}
                    {!isCashier && (
                        <button
                        onClick={() => setAddBatchModalOpen(true)}
                        className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
                        >
                        <Plus className="w-4 h-4" />
                        Add New Stock
                        </button>
                    )}
                  </div>
                  {/* Color label instruction */}
                  <div className="mb-2 flex gap-3 items-center text-xs">
                    <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold">In Stock &gt;= 10</span>
                    <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold">Low Stock &lt; 10</span>
                    <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold">Out of Stock = 0</span>
                  </div>
                  {/* Table */}
                  <div className="overflow-x-auto rounded-lg border border-gray-100">
                    <table className="w-full table-fixed text-xs">
                      <thead className="sticky top-0 bg-gray-50 z-10">
                        <tr>
                          <th className="px-3 py-2 text-left font-bold uppercase text-gray-500 w-[15%]">Batch ID</th>
                          <th className="px-3 py-2 text-left font-bold uppercase text-gray-500 w-[20%]">Made Date & Time</th>
                          <th className="px-3 py-2 text-left font-bold uppercase text-orange-600 w-[20%]">Expire Date</th>
                          <th className="px-3 py-2 text-center font-bold uppercase text-gray-500 w-[20%]">Quantity Produced</th>
                          <th className="px-3 py-2 text-left font-bold uppercase text-gray-500 w-[25%]">Notes / Description</th>
                          <th className="px-3 py-2 text-center font-bold uppercase text-gray-500 w-[10%]">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {/* Loading State */}
                        {isLoading && (
                          <tr>
                            <td colSpan={6} className="px-3 py-8 text-center">
                              <div className="flex justify-center items-center gap-2">
                                <div className="w-4 h-4 border-2 border-orange-300 border-t-orange-500 rounded-full animate-spin"></div>
                                <span className="text-gray-600">Loading batches...</span>
                              </div>
                            </td>
                          </tr>
                        )}

                        {/* Error State */}
                        {error && !isLoading && (
                          <tr>
                            <td colSpan={6} className="px-3 py-4 text-center">
                              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                <p className="text-red-700 text-sm font-medium">⚠️ {error}</p>
                              </div>
                            </td>
                          </tr>
                        )}

                        {/* Empty State */}
                        {!isLoading && !error && filteredBatches.length === 0 && (
                          <tr>
                            <td colSpan={6} className="px-3 py-8 text-center">
                              <div className="flex flex-col items-center gap-2">
                                <p className="text-gray-500 font-medium">📦 No batches found for this product</p>
                                <p className="text-gray-400 text-xs">Create a new batch to get started</p>
                              </div>
                            </td>
                          </tr>
                        )}

                        {/* Batch Rows */}
                        {!isLoading && filteredBatches.map(batch => (
                          <tr key={batch.batchId} className="border-b last:border-b-0 hover:bg-orange-50">
                            <td className="px-3 py-2 w-[15%]">{batch.batchId || 'N/A'}</td>
                            <td className="px-3 py-2 w-[20%]">{(batch.madeDate || '').replace('T', ' ')}</td>
                            <td className="px-3 py-2 font-semibold text-orange-600 w-[20%]">{(batch.expireDate || '').replace('T', ' ')}</td>
                            <td className="px-3 py-2 text-center font-bold w-[10%]">
                              {(() => {
                                const qty = Number(batch.quantity) || 0;
                                return qty === 0 ? (
                                  <span className={getQtyLabel(0)}>Out of Stock</span>
                                ) : (
                                  <span className={getQtyLabel(qty)}>{qty}</span>
                                );
                              })()}
                            </td>
                            <td className="px-3 py-2 w-[25%] truncate">{batch.notes || '-'}</td>
                            <td className="px-3 py-2 text-center">
                              {/* WASTE Button stays Visible for everyone */}
                              <button
                                className="px-2 py-1 rounded bg-orange-100 text-orange-700 font-semibold text-xs hover:bg-orange-200 transition-colors"
                                style={{ minWidth: 0, fontSize: '0.85rem', padding: '0.25rem 0.5rem' }}
                                title="Mark as Waste"
                                onClick={() => {
                                  setSelectedBatch(batch);
                                  setWastageModalOpen(true);
                                }}
                              >
                                Waste
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : null}
              <AddNewBatchModal
                open={addBatchModalOpen}
                onClose={() => setAddBatchModalOpen(false)}
                itemName={itemName}
                productId={productApiId}
                onAddBatch={handleBatchCreated}
              />
              {wastageModalOpen && selectedBatch && (
                <AddProductWastageModal
                  open={wastageModalOpen}
                  onClose={() => setWastageModalOpen(false)}
                  productData={{
                    id: productApiId!,
                    name: itemName || '',
                    currentStock: selectedBatch.currentQty,
                    unitCost: productUnitCost,
                    batchId: selectedBatch.batchId,
                    batchIdNumeric: selectedBatch.id,  // Numeric ID for API
                  }}
                  onConfirm={async () => {
                    await fetchBatches();
                    if (onStockUpdated) {
                      await onStockUpdated();
                    }
                    setWastageModalOpen(false);
                  }}
                />
              )}
            </div>
          </div>
        </div>
      );
    };