"""
Database Index Management & Verification

This script provides utilities to:
1. Verify all necessary indexes are created
2. Identify missing indexes
3. View existing indexes
4. Generate migration for missing indexes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.apps import apps
from api.models import (
    User, Category, Product, Ingredient, 
    Sale, SaleItem, Discount,
    ProductBatch, IngredientBatch,
    ProductWastage, IngredientWastage,
    ProductStockHistory, IngredientStockHistory,
    WastageReason, Notification, NotificationReceipt,
    RecipeItem
)


# ============================================================================
# INDEX DEFINITION REQUIREMENTS
# ============================================================================

REQUIRED_INDEXES = {
    'api_user': [
        {
            'fields': ['role'],
            'reason': 'Filter by user role in list endpoints'
        },
        {
            'fields': ['status'],
            'reason': 'Filter by user status (active/inactive)'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_category': [
        {
            'fields': ['type'],
            'reason': 'Filter by category type (Product/Ingredient)'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_product': [
        {
            'fields': ['product_id'],
            'reason': 'Lookup by product_id'
        },
        {
            'fields': ['category_id'],
            'reason': 'Filter products by category'
        },
        {
            'fields': ['category_id', 'name'],
            'reason': 'Unique constraint lookup'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_ingredient': [
        {
            'fields': ['ingredient_id'],
            'reason': 'Lookup by ingredient_id'
        },
        {
            'fields': ['category_id'],
            'reason': 'Filter ingredients by category'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_sale': [
        {
            'fields': ['bill_number'],
            'reason': 'Lookup by bill number'
        },
        {
            'fields': ['cashier_id'],
            'reason': 'Filter sales by cashier'
        },
        {
            'fields': ['date_time'],
            'reason': 'Filter by date/time'
        },
        {
            'fields': ['payment_method'],
            'reason': 'Filter by payment method'
        }
    ],
    'api_saleitem': [
        {
            'fields': ['sale_id'],
            'reason': 'Lookup items for a sale'
        },
        {
            'fields': ['product_id'],
            'reason': 'Lookup items by product'
        }
    ],
    'api_discount': [
        {
            'fields': ['discount_id'],
            'reason': 'Lookup by discount_id'
        },
        {
            'fields': ['is_active'],
            'reason': 'Filter active discounts'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_productbatch': [
        {
            'fields': ['product_id'],
            'reason': 'Lookup batches for product'
        },
        {
            'fields': ['expire_date'],
            'reason': 'Find expiring batches'
        }
    ],
    'api_ingredientbatch': [
        {
            'fields': ['ingredient_id'],
            'reason': 'Lookup batches for ingredient'
        },
        {
            'fields': ['expire_date'],
            'reason': 'Find expiring batches'
        }
    ],
    'api_productwastage': [
        {
            'fields': ['product_id'],
            'reason': 'Lookup wastage for product'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by date'
        }
    ],
    'api_ingredientwastage': [
        {
            'fields': ['ingredient_id'],
            'reason': 'Lookup wastage for ingredient'
        },
        {
            'fields': ['batch_id'],
            'reason': 'Lookup wastage for batch'
        }
    ],
    'api_productstockhistory': [
        {
            'fields': ['product_id'],
            'reason': 'Lookup stock history for product'
        },
        {
            'fields': ['performed_by'],
            'reason': 'Track by user'
        },
        {
            'fields': ['created_at'],
            'reason': 'Timeline queries'
        }
    ],
    'api_ingredientstockhistory': [
        {
            'fields': ['ingredient_id'],
            'reason': 'Lookup stock history for ingredient'
        },
        {
            'fields': ['batch_id'],
            'reason': 'Lookup by batch'
        },
        {
            'fields': ['created_at'],
            'reason': 'Timeline queries'
        }
    ],
    'api_notification': [
        {
            'fields': ['type'],
            'reason': 'Filter by notification type'
        },
        {
            'fields': ['created_at'],
            'reason': 'Sort by creation date'
        }
    ],
    'api_notificationreceipt': [
        {
            'fields': ['user_id'],
            'reason': 'Get notifications for user'
        },
        {
            'fields': ['is_read'],
            'reason': 'Filter unread notifications'
        },
        {
            'fields': ['user_id', 'is_read'],
            'reason': 'Get unread count for user'
        }
    ],
}


# ============================================================================
# INDEX VERIFICATION
# ============================================================================

def get_existing_indexes():
    """Get all existing indexes from database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        return cursor.fetchall()


def verify_indexes():
    """Verify all required indexes exist"""
    print("=" * 80)
    print("DATABASE INDEX VERIFICATION REPORT")
    print("=" * 80)
    
    existing = get_existing_indexes()
    
    # Check Models
    models_to_check = [
        User, Category, Product, Ingredient,
        Sale, SaleItem, Discount,
        ProductBatch, IngredientBatch,
        ProductWastage, IngredientWastage,
        ProductStockHistory, IngredientStockHistory,
        WastageReason, Notification, NotificationReceipt,
        RecipeItem
    ]
    
    missing_optimal_indexes = []
    
    for model in models_to_check:
        table_name = model._meta.db_table
        
        # Get model's defined indexes
        meta_indexes = getattr(model._meta, 'indexes', [])
        
        print(f"\n✓ {model.__name__} ({table_name})")
        print(f"  Defined Indexes: {len(meta_indexes)}")
        
        for idx in meta_indexes:
            fields = ', '.join(idx.fields) if hasattr(idx, 'fields') else str(idx)
            print(f"    - {fields}")
        
        # Check for missing recommended indexes
        if table_name in REQUIRED_INDEXES:
            for idx_config in REQUIRED_INDEXES[table_name]:
                fields = idx_config['fields']
                reason = idx_config['reason']
                
                # Check if this index exists
                fields_str = ', '.join(str(f) for f in fields)
                index_found = any(fields_str in idx_def for _, _, idx_def in existing)
                
                if not index_found:
                    missing_optimal_indexes.append({
                        'table': table_name,
                        'fields': fields,
                        'reason': reason,
                        'model': model.__name__
                    })
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if missing_optimal_indexes:
        print(f"\n⚠ Found {len(missing_optimal_indexes)} recommended indexes that could improve performance:\n")
        
        for idx in missing_optimal_indexes:
            print(f"◦ {idx['model']} - {', '.join(idx['fields'])}")
            print(f"  Reason: {idx['reason']}\n")
        
        print("To add these indexes, update the model's Meta class:")
        print("""
        class Meta:
            indexes = [
                models.Index(fields=['field1']),
                models.Index(fields=['field1', 'field2']),  # Composite index
            ]
        
        Then run:
        python manage.py makemigrations
        python manage.py migrate
        """)
    else:
        print("\n✓ All recommended indexes are in place!")
    
    print("\n" + "=" * 80)


def get_query_statistics():
    """Get database query statistics"""
    print("\n" + "=" * 80)
    print("QUERY STATISTICS (from current session)")
    print("=" * 80)
    
    # Count queries if in debug mode (typically for testing)
    from django.test.utils import CaptureQueriesContext
    from django.db import connection as db_connection
    
    print("\nTo view query statistics during testing:")
    print("""
    from django.test.utils import CaptureQueriesContext
    from django.db import connection
    
    with CaptureQueriesContext(connection) as captured:
        # Run your code here
        pass
    
    print(f"Executed {len(captured)} queries")
    for query in captured:
        print(f"  - {query['sql']}")
        print(f"    Time: {query['time']}s")
    """)


if __name__ == '__main__':
    verify_indexes()
    get_query_statistics()
    
    print("\n" + "=" * 80)
    print("✓ INDEX VERIFICATION COMPLETE")
    print("=" * 80)
