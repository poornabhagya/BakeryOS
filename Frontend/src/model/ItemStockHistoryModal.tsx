import React, { useState } from 'react';
import { X, ArrowLeft, Plus, Search } from 'lucide-react';
import { AddNewBatchModal } from './AddNewBatchModal';

// Mock batch data
const initialBatches = [
	{
		batchId: '#BATCH-001',
		madeDate: '2026-01-22T08:00',
		expireDate: '2026-01-24T08:00',
		quantity: 120,
		status: 'In Stock',
		notes: 'Morning batch, fresh.',
	},
	{
		batchId: '#BATCH-002',
		madeDate: '2026-01-21T15:00',
		expireDate: '2026-01-23T15:00',
		quantity: 20,
		status: 'Low Stock',
		notes: 'Afternoon batch, almost sold out.',
	},
	{
		batchId: '#BATCH-003',
		madeDate: '2026-01-20T09:00',
		expireDate: '2026-01-22T09:00',
		quantity: 0,
		status: 'Expired',
		notes: 'Expired batch.',
	},
];

const statusStyles = {
	'In Stock': 'bg-green-100 text-green-700',
	'Low Stock': 'bg-yellow-100 text-yellow-700',
	'Expired': 'bg-red-100 text-red-700',
};

function generateBatchId() {
	return `#BATCH-${Math.floor(1000 + Math.random() * 9000)}`;
}

interface ItemStockHistoryModalProps {
	open: boolean;
	onClose: () => void;
	itemName?: string;
	itemId?: string;
}

type Batch = {
	batchId: string;
	madeDate: string;
	expireDate: string;
	quantity: number;
	status: string;
	notes: string;
};

const ItemStockHistoryModal = ({ open, onClose, itemName, itemId }: ItemStockHistoryModalProps) => {
	const [view, setView] = useState<'list' | 'add'>('list');
	// ...rest of the component implementation...
	return null;
};

export default ItemStockHistoryModal;
