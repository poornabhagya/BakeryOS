# AddItemModal Recipe Items Debug Guide

## What Changed

The `handleSave` function in `AddItemModal.tsx` now includes DETAILED console logging to help diagnose why recipe items aren't being saved. 

## Steps to Test

### 1. Open Browser Developer Tools
- Press **F12** or Right-click → Inspect → Console tab

### 2. Open the Add Product Modal
- Click "Add Product" button in Stock Management screen

### 3. Look for Initial Logs
In the browser console, you should see:
```
[AddItemModal] Received ingredients prop: (Array)
  (Shows all available ingredients with their IDs)
```

If you see: `[AddItemModal] WARNING - No ingredients prop or empty array!`
→ **Issue**: Ingredients aren't being passed from parent component. Stop here and report this.

### 4. Fill Out the Form
- Enter Product Name: e.g., "Test Recipe Product"
- Select Category
- Enter Shelf Life and Unit
- Enter Cost Price (e.g., 50)
- Enter Selling Price (e.g., 100)

### 5. ADD RECIPE INGREDIENTS (Critical Step)
- Click "Add Ingredient" button
- Select an ingredient from dropdown (e.g., "Baking Powder")
- Enter a quantity (e.g., 2.5)
- **Keep looking at console while doing this** - you should see logs like:

```
[AddItemModal] handleRecipeChange - idx: 0, field: ingredientId, value: "13"
[AddItemModal] Ingredient selected: id=13, name=Baking Powder, unit=kg
[AddItemModal] Updated row 0: {ingredientId: "13", quantity: "", unit: "kg"}
[AddItemModal] New recipeRows state after change: (Array)
```

Then when you enter quantity:
```
[AddItemModal] handleRecipeChange - idx: 0, field: quantity, value: "2.5"
[AddItemModal] Updated row 0 (quantity): {ingredientId: "13", quantity: "2.5", unit: "kg"}
```

### 6. Submit the Form - THIS IS THE KEY MOMENT
Click "Save Product" button and watch the console carefully.

You should see a LARGE output like:

```
[AddItemModal] ===== FORM SUBMISSION START =====
[AddItemModal] Current recipeRows state: (Array)
  [0]: {ingredientId: "13", quantity: "2.5", unit: "kg"}
  
[AddItemModal] Basic field validation passed

[AddItemModal] Price parsing passed: {costPriceNum: 50, sellingPriceNum: 100}

[AddItemModal] Before filtering - recipeRows: (Array)

[AddItemModal] Row filtering - ingredientId: "13" (has: true), quantity: "2.5" (has: true)

[AddItemModal] After filtering - filteredRows count: 1

[AddItemModal] Filtered rows data: (Array)
  [0]: {ingredientId: "13", quantity: "2.5", unit: "kg"}

[AddItemModal] Mapping row 0: ingredientId=13 (from "13"), quantity=2.5 (from "2.5")

[AddItemModal] Final recipeItems array: (Array)
  [0]: {ingredient_id: 13, quantity_required: 2.5}

[AddItemModal] ===== FINAL PAYLOAD =====
[AddItemModal] Submitting payload: {
  "name": "Test Recipe Product",
  "category_id": 2,
  "cost_price": 50,
  "selling_price": 100,
  "shelf_life": 5,
  "shelf_unit": "days",
  "preparation_instructions": null,
  "current_stock": 0,
  "recipe_items": [
    {
      "ingredient_id": 13,
      "quantity_required": 2.5
    }
  ]
}

[AddItemModal] Payload has recipe_items: true
[AddItemModal] recipe_items is array: true
[AddItemModal] recipe_items length: 1
```

### 7. What To Look For

#### ✅ **CORRECT** - You should see:
- `recipe_items` array in the final payload
- `recipe_items length: 1` (or however many ingredients you added)
- Each item has `ingredient_id` (number) and `quantity_required` (number)

#### ❌ **PROBLEM** - If you see:
- `recipe_items length: 0` → Rows were filtered out (check if ingredient or quantity were empty)
- No `recipe_items` field in payload → Something went wrong in the code
- `ingredientId=NaN` → The ingredient ID couldn't be converted to a number
- Row filtering shows: `(has: false)` → Either ingredientId or quantity was empty when you submitted

### 8. Check if API Actually Received It
After submission, if the product was created, check Django admin:
- Go to Django Admin → Recipe Items
- Look for your new product
- Recipe items should be listed there with ingredient_id and quantity_required

### 9. Report What You Find

Copy-paste the console output showing:
1. The FINAL PAYLOAD section
2. Any error messages
3. Whether recipe_items array was included
4. The length of recipe_items
