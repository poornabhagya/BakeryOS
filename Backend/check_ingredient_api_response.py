#!/usr/bin/env python
"""Check what the ingredient API actually returns"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Ingredient

# Get first ingredient as it would appear in API
ing = Ingredient.objects.first()
if ing:
    # This is what the GET endpoint returns
    data = {
        'id': ing.id,
        'ingredient_id': ing.ingredient_id,
        'name': ing.name,
        'category_name': ing.category_id.name if ing.category_id else None,
        'base_unit': ing.base_unit,
        'total_quantity': str(ing.total_quantity),
        'tracking_type': ing.tracking_type,
        'low_stock_threshold': ing.low_stock_threshold,
        'supplier': ing.supplier,
        'supplier_contact': ing.supplier_contact,
        'is_active': ing.is_active,
    }
    print('API returns:')
    print(json.dumps(data, indent=2, default=str))
    
    print()
    print('Frontend receives:')
    obtained_id = data.get('ingredient_id') or data.get('id')
    print(f'  ing.id = {obtained_id}')
    print(f'  Type: {type(obtained_id).__name__}')
