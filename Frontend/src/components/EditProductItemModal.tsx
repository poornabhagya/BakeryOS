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

export const EditProductItemModal: React.FC<EditProductItemModalProps> = ({ isOpen, onClose, itemToEdit }) => {
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
      setRecipe(
        itemToEdit.recipe && itemToEdit.recipe.length > 0
          ? itemToEdit.recipe.map(row => ({
              id: row.id,
              ingredientId: row.ingredientId,
              qty: row.qty,
              unit: row.unit,
            }))
          : [{ ...initialRecipeRow }]
      );
    }
  }, [isOpen, itemToEdit]);

  // Recipe table handlers
  const handleRecipeChange = (idx: number, field: keyof RecipeRow, value: string | number) => {
    setRecipe(prev => prev.map((row, i) => {
      if (i !== idx) return row;
      if (field === 'ingredientId') {
        const found = INGREDIENTS.find(ing => ing.id === value);
        return { ...row, ingredientId: value as string, unit: found ? found.unit : '', qty: '' };
      }
      return { ...row, [field]: value };
    }));
  };

  const handleAddRecipeRow = () => {
    setRecipe(prev => [...prev, { ...initialRecipeRow }]);
  };

  const handleRemoveRecipeRow = (idx: number) => {
    setRecipe(prev => prev.length === 1 ? prev : prev.filter((_, i) => i !== idx));
  };

  // Profit calculation
  const profitMargin =
    costPrice && sellingPrice && !isNaN(Number(costPrice)) && !isNaN(Number(sellingPrice))
      ? `${(((Number(sellingPrice) - Number(costPrice)) / Number(costPrice)) * 100).toFixed(1)}%`
      : null;

  // Save/Update handler
  const handleUpdate = () => {
    // TODO: Implement update logic (API call, state update, etc.)
    onClose && onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg h-[85vh] z-[100] bg-white text-orange-900 overflow-y-auto">
        <DialogDescription asChild>
          <span className="sr-only" id="edit-item-modal-desc">Edit product details and recipe.</span>
        </DialogDescription>
        <DialogHeader className="mb-2">
          <div className="flex items-center gap-3">
            <DialogTitle className="text-2xl font-bold">Edit Product Item</DialogTitle>
            <Badge className="bg-orange-500 text-white">Product</Badge>
          </div>
        </DialogHeader>
        {/* Basic Details */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Item ID</label>
            <Input value={itemId} readOnly className="bg-orange-50" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1">Item Name</label>
            <Input value={itemName} onChange={e => setItemName(e.target.value)} placeholder="e.g. Fish Bun" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger className="w-full bg-orange-50">
                <SelectValue placeholder="Select Category" />
              </SelectTrigger>
              <SelectContent>
                {CATEGORIES.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><Clock size={16} /> Shelf Life</label>
            <div className="flex gap-2">
              <Input value={shelfLife} onChange={e => setShelfLife(e.target.value)} placeholder="e.g. 2" className="w-20" />
              <Select value={shelfLifeUnit} onValueChange={setShelfLifeUnit}>
                <SelectTrigger className="w-24 bg-orange-50">
                  <SelectValue placeholder="Unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Days">Days</SelectItem>
                  <SelectItem value="Hours">Hours</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </section>
        {/* Pricing */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><DollarSign size={16} /> Cost Price (Rs.)</label>
            <Input type="number" min="0" value={costPrice} onChange={e => setCostPrice(e.target.value)} placeholder="0.00" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 flex items-center gap-1"><DollarSign size={16} /> Selling Price (Rs.)</label>
            <Input type="number" min="0" value={sellingPrice} onChange={e => setSellingPrice(e.target.value)} placeholder="0.00" />
          </div>
          <div className="flex items-end">
            {profitMargin && (
              <Badge className="bg-orange-400 text-white">Recalculate Profit: {profitMargin}</Badge>
            )}
          </div>
        </section>
        {/* Recipe & Ingredients */}
        <section className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-semibold text-lg">Recipe & Ingredients</span>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full border rounded-lg">
              <thead className="bg-orange-100">
                <tr>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Ingredient</th>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Quantity</th>
                  <th className="px-3 py-2 text-left text-sm font-semibold">Unit</th>
                  <th className="px-3 py-2"></th>
                </tr>
              </thead>
              <tbody>
                {recipe.map((row, idx) => (
                  <tr key={idx} className="border-b last:border-b-0">
                    <td className="px-3 py-2">
                      <Select
                        value={row.ingredientId}
                        onValueChange={(val: string) => handleRecipeChange(idx, 'ingredientId', val)}
                      >
                        <SelectTrigger className="w-40 bg-orange-50">
                          <SelectValue placeholder="Select Ingredient" />
                        </SelectTrigger>
                        <SelectContent>
                          {INGREDIENTS.map(ing => (
                            <SelectItem key={ing.id} value={ing.id}>{ing.name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                    <td className="px-3 py-2">
                      <Input
                        type="number"
                        min="0"
                        value={row.qty}
                        onChange={e => handleRecipeChange(idx, 'qty', e.target.value)}
                        disabled={!row.ingredientId}
                        placeholder="0"
                        className="w-24"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <span className="inline-block min-w-[2.5rem]">{row.unit}</span>
                    </td>
                    <td className="px-3 py-2">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="text-red-500 hover:bg-red-100"
                        onClick={() => handleRemoveRecipeRow(idx)}
                        disabled={recipe.length === 1}
                        aria-label="Remove Ingredient"
                      >
                        <Trash size={18} />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Button
            type="button"
            variant="outline"
            className="mt-3 flex items-center gap-2 text-orange-600 border-orange-300 hover:bg-orange-50"
            onClick={handleAddRecipeRow}
          >
            <Plus size={18} /> Add Ingredient Line
          </Button>
        </section>
        {/* Footer */}
        <DialogFooter className="flex flex-row gap-3 justify-end">
          <Button variant="outline" onClick={onClose} className="border-orange-300 text-orange-600">Cancel</Button>
          <Button onClick={handleUpdate} className="bg-orange-500 hover:bg-orange-600 text-white">Update Product</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EditProductItemModal;
