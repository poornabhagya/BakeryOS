import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, r'c:\Projects\campus project\BakeryOS_Project\Backend')
django.setup()

from django.db import connection
from api.models import SaleItem, Product

print("[STEP 1] Checking for NULL product_id in SaleItem...")
null_items = SaleItem.objects.filter(product_id__isnull=True)
print(f"Found {null_items.count()} items with NULL product_id")

if null_items.exists():
    print("[STEP 2] Deleting NULL product_id items (they are invalid)...")
    deleted_count, _ = null_items.delete()
    print(f"Deleted {deleted_count} items")

print("[STEP 3] Running makemigrations...")
from django.core.management import call_command
call_command('makemigrations', 'api', interactive=False)

print("[STEP 4] Running migrate...")
call_command('migrate', interactive=False)

print("[SUCCESS] All migrations applied! ProductBatch.current_qty field is now available.")
