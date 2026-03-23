from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User


@receiver(pre_save, sender=User)
def generate_employee_id(sender, instance, **kwargs):
    """
    Auto-generate employee_id if not provided.
    Format: EMP-001, EMP-002, EMP-003, etc.
    """
    if not instance.employee_id:
        # Get the highest existing employee_id number
        last_user = User.objects.filter(
            employee_id__startswith='EMP-'
        ).order_by('employee_id').last()
        
        if last_user and last_user.employee_id:
            # Extract number from last employee_id (e.g., "EMP-001" -> 1)
            try:
                last_number = int(last_user.employee_id.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            # No employees exist yet, start with 1
            new_number = 1
        
        # Format with leading zeros (3 digits)
        instance.employee_id = f'EMP-{new_number:03d}'


# Product signal - Registered after models are fully loaded
def setup_product_signals():
    """Register Product signals after app is ready"""
    from .models import Product
    
    @receiver(pre_save, sender=Product)
    def auto_generate_product_id(sender, instance, **kwargs):
        """
        Auto-generate product_id if not already set.
        Format: #PROD-1001, #PROD-1002, etc.
        """
        if not instance.product_id:
            # Get the last product_id sequence number
            last_product = Product.objects.filter(
                product_id__startswith='#PROD-'
            ).order_by('-product_id').first()
            
            if last_product:
                # Extract sequence number and increment
                try:
                    seq = int(last_product.product_id.split('-')[1])
                    next_seq = seq + 1
                except (IndexError, ValueError):
                    next_seq = 1001
            else:
                # Start from 1001
                next_seq = 1001
            
            instance.product_id = f'#PROD-{next_seq}'
