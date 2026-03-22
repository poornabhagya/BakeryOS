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
