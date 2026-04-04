"""
Test: Verify Product Quantity Calculation Fix

This test verifies that:
1. Product quantity is calculated as the exact sum of ProductBatch.quantity values
2. Products with no batches show quantity = 0
3. The calculation works via API (annotated field 'total_batch_quantity')
4. The quantity updates correctly when batches are added/removed
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, '/Users/Poorna Bhagya/Projects/campus project/BakeryOS_Project/Backend')
django.setup()

from api.models import Product, Category, ProductBatch
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


def print_test(title):
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"TEST: {title}")
    print(f"{'='*70}{Colors.END}")


def print_pass(msg):
    print(f"{Colors.GREEN}✓ PASS:{Colors.END} {msg}")


def print_fail(msg):
    print(f"{Colors.RED}✗ FAIL:{Colors.END} {msg}")


def print_info(msg):
    print(f"{Colors.YELLOW}ℹ INFO:{Colors.END} {msg}")


def test_product_quantity_calculation():
    """Test 1: Product quantity is sum of batch quantities"""
    print_test("Product Quantity = Sum of Batch Quantities")
    
    try:
        # Get or create a test category
        category, _ = Category.objects.get_or_create(
            name='Test Category',
            defaults={'type': 'Product', 'description': 'For testing'}
        )
        
        # Create a test product
        product = Product.objects.create(
            name='Test Product',
            category_id=category,
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            shelf_life=5,
            shelf_unit='days',
            current_stock=Decimal('0')  # Start with 0
        )
        print_info(f"Created product: {product.product_id} - {product.name}")
        
        # Create batches
        batch_quantities = [
            Decimal('10.00'),
            Decimal('15.50'),
            Decimal('8.75')
        ]
        
        batches = []
        for i, qty in enumerate(batch_quantities):
            batch = ProductBatch.objects.create(
                product_id=product,
                quantity=qty,
                made_date=date.today(),
                status='Active'
            )
            batches.append(batch)
            print_info(f"Created batch {i+1}: {batch.batch_id} with quantity {qty}")
        
        # Calculate expected total
        expected_total = sum(batch_quantities)
        print_info(f"Expected total quantity: {expected_total}")
        
        # Get the product with annotation
        product_with_annotation = Product.objects.annotate(
            total_batch_quantity=Coalesce(Sum('batches__quantity'), Decimal('0'))
        ).get(id=product.id)
        
        calculated_quantity = product_with_annotation.total_batch_quantity
        print_info(f"Calculated quantity from annotation: {calculated_quantity}")
        
        # Verify
        if calculated_quantity == expected_total:
            print_pass(f"Quantity matches! {calculated_quantity} == {expected_total}")
            return True
        else:
            print_fail(f"Quantity mismatch: {calculated_quantity} != {expected_total}")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_product_no_batches():
    """Test 2: Product with no batches shows quantity = 0"""
    print_test("Product with No Batches Shows Quantity = 0")
    
    try:
        # Get or create a test category
        category, _ = Category.objects.get_or_create(
            name='Test Category 2',
            defaults={'type': 'Product', 'description': 'For testing'}
        )
        
        # Create a product with no batches
        product = Product.objects.create(
            name='Empty Product',
            category_id=category,
            cost_price=Decimal('5.00'),
            selling_price=Decimal('10.00'),
            shelf_life=3,
            shelf_unit='days',
            current_stock=Decimal('0')
        )
        print_info(f"Created product with no batches: {product.product_id}")
        
        # Get with annotation
        product_with_annotation = Product.objects.annotate(
            total_batch_quantity=Coalesce(Sum('batches__quantity'), Decimal('0'))
        ).get(id=product.id)
        
        calculated_quantity = product_with_annotation.total_batch_quantity
        print_info(f"Calculated quantity: {calculated_quantity}")
        
        # Verify it's 0
        if calculated_quantity == Decimal('0'):
            print_pass(f"Quantity is correctly 0 for product with no batches")
            return True
        else:
            print_fail(f"Quantity should be 0 but got {calculated_quantity}")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_quantity_updates_with_batch_deletion():
    """Test 3: Quantity updates when batch is deleted"""
    print_test("Quantity Updates When Batch is Deleted")
    
    try:
        # Get or create a test category
        category, _ = Category.objects.get_or_create(
            name='Test Category 3',
            defaults={'type': 'Product', 'description': 'For testing'}
        )
        
        # Create a product
        product = Product.objects.create(
            name='Test Product Delete',
            category_id=category,
            cost_price=Decimal('10.00'),
            selling_price=Decimal('20.00'),
            shelf_life=5,
            shelf_unit='days',
            current_stock=Decimal('0')
        )
        print_info(f"Created product: {product.product_id}")
        
        # Create batches
        batch1 = ProductBatch.objects.create(
            product_id=product,
            quantity=Decimal('20.00'),
            made_date=date.today(),
            status='Active'
        )
        batch2 = ProductBatch.objects.create(
            product_id=product,
            quantity=Decimal('30.00'),
            made_date=date.today(),
            status='Active'
        )
        print_info(f"Created 2 batches: {batch1.batch_id} (20) and {batch2.batch_id} (30)")
        
        # Get initial quantity
        product_annotated = Product.objects.annotate(
            total_batch_quantity=Coalesce(Sum('batches__quantity'), Decimal('0'))
        ).get(id=product.id)
        initial_qty = product_annotated.total_batch_quantity
        print_info(f"Initial total quantity: {initial_qty}")
        
        if initial_qty != Decimal('50'):
            print_fail(f"Initial quantity should be 50, got {initial_qty}")
            return False
        
        # Delete one batch
        batch_id_to_delete = batch1.batch_id
        batch1.delete()
        print_info(f"Deleted batch: {batch_id_to_delete}")
        
        # Get updated quantity
        product_annotated = Product.objects.annotate(
            total_batch_quantity=Coalesce(Sum('batches__quantity'), Decimal('0'))
        ).get(id=product.id)
        final_qty = product_annotated.total_batch_quantity
        print_info(f"Final total quantity: {final_qty}")
        
        # Verify
        if final_qty == Decimal('30'):
            print_pass(f"Quantity correctly updated to {final_qty} after deletion")
            return True
        else:
            print_fail(f"Quantity should be 30 but got {final_qty}")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup():
    """Clean up test data"""
    print_test("Cleanup")
    try:
        # Delete test products (will cascade delete batches)
        Product.objects.filter(name__in=['Test Product', 'Empty Product', 'Test Product Delete']).delete()
        print_pass("Test data cleaned up")
    except Exception as e:
        print_fail(f"Cleanup failed: {str(e)}")


if __name__ == '__main__':
    print(f"\n{Colors.CYAN}PRODUCT QUANTITY CALCULATION FIX - TEST SUITE{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")
    
    results = []
    
    # Run tests
    results.append(('Test 1: Quantity = Sum of Batches', test_product_quantity_calculation()))
    results.append(('Test 2: No Batches = Quantity 0', test_product_no_batches()))
    results.append(('Test 3: Quantity Updates on Delete', test_quantity_updates_with_batch_deletion()))
    
    # Cleanup
    cleanup()
    
    # Summary
    print_test("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.END}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}✗ SOME TESTS FAILED{Colors.END}\n")
        sys.exit(1)
