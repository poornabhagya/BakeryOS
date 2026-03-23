#!/usr/bin/env python
"""Verify Product migration status"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

print("=" * 70)
print("MIGRATION STATUS CHECK".center(70))
print("=" * 70)

# Check if Product table exists
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='api_product'
    """)
    table_exists = cursor.fetchone() is not None

if table_exists:
    print("\n✓ Product table EXISTS in database")
    
    # Get row count
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM api_product")
        count = cursor.fetchone()[0]
        print(f"  Product records: {count}")
else:
    print("\n✗ Product table NOT found - applying migrations...")
    
    # Apply migrations
    try:
        call_command('migrate', verbosity=0)
        print("✓ Migrations applied successfully")
        
        # Verify again
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM api_product")
            print(f"✓ Product table now exists")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)

print("\n" + "=" * 70)
print("Ready to start server: python manage.py runserver 8000".center(70))
print("=" * 70 + "\n")
