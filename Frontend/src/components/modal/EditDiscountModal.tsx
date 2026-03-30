import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Loader } from 'lucide-react';

interface Discount {
  id: string;
  name: string;
  type: 'percentage' | 'fixed';
  value: number;
  applicableTo: 'all' | 'category' | 'item';
  targetId?: string;
  startDate?: string;
  endDate?: string;
  startTime?: string;
  endTime?: string;
}

interface EditDiscountModalProps {
  open: boolean;
  onClose: () => void;
  discount: Discount | null;
  onUpdate: (updatedDiscount: Discount) => Promise<void>;
  categories: string[];
  items: { id: string; name: string }[];
}

const DISCOUNT_TYPES = [
  { label: 'Percentage', value: 'percentage', symbol: '%' },
  { label: 'Fixed Amount', value: 'fixed', symbol: 'Rs.' },
];

const APPLICABLE_TO = [
  { label: 'All Items', value: 'all' },
  { label: 'Specific Category', value: 'category' },
  { label: 'Specific Item', value: 'item' },
];

export const EditDiscountModal: React.FC<EditDiscountModalProps> = ({ open, onClose, discount, onUpdate, categories, items }) => {
  const [name, setName] = useState('');
  const [type, setType] = useState<'percentage' | 'fixed'>('percentage');
  const [value, setValue] = useState<number | ''>('');
  const [applicableTo, setApplicableTo] = useState<'all' | 'category' | 'item'>('all');
  const [category, setCategory] = useState('');
  const [item, setItem] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [touched, setTouched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (open && discount) {
      setName(discount.name || '');
      setType(discount.type);
      setValue(discount.value);
      setApplicableTo(discount.applicableTo);
      if (discount.applicableTo === 'category') setCategory(discount.targetId || '');
      else setCategory('');
      if (discount.applicableTo === 'item') setItem(discount.targetId || '');
      else setItem('');
      setStartDate(discount.startDate || '');
      setEndDate(discount.endDate || '');
      setStartTime(discount.startTime || '');
      setEndTime(discount.endTime || '');
      setTouched(false);
    }
  }, [open, discount]);

  const valueInvalid = value === '' || Number(value) <= 0;
  const nameInvalid = !name.trim();
  const canUpdate = !nameInvalid && !valueInvalid && (applicableTo !== 'category' || category) && (applicableTo !== 'item' || item);

  if (!open || !discount) return null;

  const handleUpdate = async () => {
    setTouched(true);
    if (!canUpdate) return;
    
    setIsLoading(true);
    try {
      await onUpdate({
        id: discount.id,
        name: name.trim(),
        type,
        value: Number(value),
        applicableTo,
        targetId: applicableTo === 'category' ? category : applicableTo === 'item' ? item : undefined,
        startDate: startDate || undefined,
        endDate: endDate || undefined,
        startTime: startTime || undefined,
        endTime: endTime || undefined,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" aria-modal="true" role="dialog">
      <div className="bg-white w-full max-w-lg rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
          <h3 className="text-lg font-bold text-orange-800">Edit Discount - {discount.id}</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        {/* Body */}
        <div className="flex-1 p-6 flex flex-col gap-5">
          {/* Discount ID (read-only) */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Discount ID</label>
            <input
              type="text"
              value={discount.id}
              readOnly
              disabled
              className="w-full bg-gray-100 text-gray-500 rounded-lg px-3 py-2 border border-gray-200 cursor-not-allowed"
            />
          </div>
          {/* Discount Name */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Discount Name <span className="text-red-500">*</span></label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              placeholder="e.g. Evening Happy Hour"
              required
            />
            {touched && nameInvalid && <p className="text-xs text-red-500 mt-1">Discount name is required.</p>}
          </div>
          {/* Discount Type & Value */}
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700">Type</label>
              <select
                value={type}
                onChange={e => setType(e.target.value as 'percentage' | 'fixed')}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              >
                {DISCOUNT_TYPES.map(dt => (
                  <option key={dt.value} value={dt.value}>{dt.label}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700">Value <span className="text-red-500">*</span></label>
              <div className="flex items-center border border-gray-300 rounded-lg px-2 focus-within:ring-2 focus-within:ring-orange-500 focus-within:border-transparent transition-all bg-white">
                {type === 'fixed' && <span className="text-gray-400 mr-1">Rs.</span>}
                <input
                  type="number"
                  min={1}
                  value={value}
                  onChange={e => setValue(e.target.value === '' ? '' : Number(e.target.value))}
                  className="flex-1 px-2 py-2 bg-transparent outline-none"
                  placeholder={type === 'percentage' ? 'e.g. 10' : 'e.g. 100'}
                  required
                />
                {type === 'percentage' && <span className="text-gray-400 ml-1">%</span>}
              </div>
              {touched && valueInvalid && <p className="text-xs text-red-500 mt-1">Enter a valid discount value.</p>}
            </div>
          </div>
          {/* Applicable To */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Applicable To</label>
            <div className="flex gap-4 mb-2">
              {APPLICABLE_TO.map(opt => (
                <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="applicableToEdit"
                    value={opt.value}
                    checked={applicableTo === opt.value}
                    onChange={() => setApplicableTo(opt.value as 'all' | 'category' | 'item')}
                    className="accent-orange-500"
                  />
                  <span className="text-gray-700 text-sm">{opt.label}</span>
                </label>
              ))}
            </div>
            {applicableTo === 'category' && (
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              >
                <option value="">Select Category</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            )}
            {applicableTo === 'item' && (
              <select
                value={item}
                onChange={e => setItem(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              >
                <option value="">Select Item</option>
                {items.map(it => (
                  <option key={it.id} value={it.id}>{it.name}</option>
                ))}
              </select>
            )}
          </div>
          {/* Validity Period */}
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1 text-gray-700">End Date <span className="text-xs text-gray-400">(optional)</span></label>
              <input
                type="date"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              />
              {endDate && <button type="button" className="text-xs text-orange-500 mt-1 ml-1" onClick={() => setEndDate('')}>Clear</button>}
            </div>
          </div>
          {/* Happy Hour (Time) */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Happy Hour (Time) <span className="text-xs text-gray-400">(optional)</span></label>
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <input
                  type="time"
                  value={startTime}
                  onChange={e => setStartTime(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                />
              </div>
              <div className="flex-1">
                <input
                  type="time"
                  value={endTime}
                  onChange={e => setEndTime(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
            <div className="text-xs text-gray-400 mt-1">Leave empty for all-day validity.</div>
          </div>
        </div>
        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-orange-100 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleUpdate}
            disabled={!canUpdate || isLoading}
            className="px-4 py-2 rounded-lg bg-orange-600 text-white font-bold hover:bg-orange-700 transition-colors disabled:opacity-60 flex items-center gap-2"
          >
            {isLoading && <Loader className="w-4 h-4 animate-spin" />}
            {isLoading ? 'Updating...' : 'Update Discount'}
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
