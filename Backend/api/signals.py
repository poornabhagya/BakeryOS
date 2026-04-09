from django.db.models.signals import pre_save, post_save, post_delete
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


# Stock History signals for audit trail tracking
def setup_stock_history_signals():
    """Register stock history signals after models are loaded"""
    from .models import ProductWastage, IngredientWastage, IngredientBatch, ProductStockHistory, IngredientStockHistory
    
    @receiver(post_save, sender=ProductWastage)
    def create_product_stock_history_on_wastage(sender, instance, created, **kwargs):
        """
        Auto-create ProductStockHistory entry when ProductWastage is recorded.
        
        Tracks product wastage as a stock deduction in the audit trail.
        """
        if created:
            product = instance.product_id
            qty_after = product.current_stock
            qty_before = qty_after + instance.quantity
            
            ProductStockHistory.objects.create(
                product_id=product,
                transaction_type='WasteStock',
                qty_before=qty_before,
                qty_after=qty_after,
                change_amount=-instance.quantity,
                user_id=instance.reported_by,
                notes=f"Wastage: {instance.reason_id.reason}. {instance.notes if instance.notes else ''}".strip(),
            )
    
    @receiver(post_save, sender=IngredientBatch)
    def create_ingredient_stock_history_on_batch_create(sender, instance, created, **kwargs):
        """
        Auto-create IngredientStockHistory entry when IngredientBatch is created.
        
        Tracks adding new ingredient stock from batch receipt.
        """
        if created:
            ingredient = instance.ingredient_id
            qty_after = ingredient.total_quantity
            qty_before = qty_after - instance.quantity
            
            IngredientStockHistory.objects.create(
                ingredient_id=ingredient,
                batch_id=instance,
                transaction_type='AddStock',
                qty_before=qty_before,
                qty_after=qty_after,
                change_amount=instance.quantity,
                reference_id=instance.batch_id,
                notes=f"New batch from {ingredient.supplier}. Total batch cost: {instance.total_batch_cost}",
            )
    
    @receiver(post_delete, sender=IngredientBatch)
    def create_ingredient_stock_history_on_batch_delete(sender, instance, **kwargs):
        """
        Auto-create IngredientStockHistory entry when IngredientBatch is deleted.
        
        Tracks removing ingredient stock when batch is removed from system.
        """
        ingredient = instance.ingredient_id
        qty_after = ingredient.total_quantity
        qty_before = qty_after + instance.quantity
        
        IngredientStockHistory.objects.create(
            ingredient_id=ingredient,
            batch_id=instance,
            transaction_type='UseStock',
            qty_before=qty_before,
            qty_after=qty_after,
            change_amount=-instance.quantity,
            reference_id=instance.batch_id,
            notes=f"Batch removed from system ({instance.status} status)",
        )
    
    @receiver(post_save, sender=IngredientWastage)
    def create_ingredient_stock_history_on_wastage(sender, instance, created, **kwargs):
        """
        Auto-create IngredientStockHistory entry when IngredientWastage is recorded.
        
        Tracks ingredient wastage as a stock deduction/loss in audit trail.
        """
        if created:
            ingredient = instance.ingredient_id
            batch = instance.batch_id
            
            qty_after = ingredient.total_quantity if not batch else batch.current_qty
            qty_before = qty_after + instance.quantity
            
            IngredientStockHistory.objects.create(
                ingredient_id=ingredient,
                batch_id=batch,
                transaction_type='Wastage',
                qty_before=qty_before,
                qty_after=qty_after,
                change_amount=-instance.quantity,
                performed_by=instance.reported_by,
                reference_id=instance.wastage_id,
                notes=f"Wastage: {instance.reason_id.reason}. {instance.notes if instance.notes else ''}".strip(),
            )


# Notification signals - Create notifications on specific events
def setup_notification_signals():
    """Register notification signals after models are loaded"""
    from .models import (
        Notification, NotificationReceipt, ProductWastage, 
        IngredientWastage, IngredientBatch, Product, Ingredient
    )
    from django.utils import timezone
    from datetime import timedelta
    
    @receiver(post_save, sender=IngredientBatch)
    def check_expiry_notification(sender, instance, created, **kwargs):
        """
        Create notification when ingredient batch is expiring soon (within 2 days).
        """
        if not created:
            return
        
        if instance.expire_date:
            expire_date = instance.expire_date.date() if hasattr(instance.expire_date, 'date') else instance.expire_date
            days_until_expiry = (expire_date - timezone.now().date()).days
            
            if days_until_expiry <= 2:
                # Create notification for storekeeper and manager
                notification = Notification.objects.create(
                    title=f"Expiring Soon: {instance.ingredient_id.name}",
                    message=f"Batch {instance.batch_id} ({instance.quantity} {instance.ingredient_id.base_unit}) expires on {instance.expire_date}",
                    type='Expiry',
                    icon='alert'
                )
                
                # Send to Storekeeper and Manager roles
                users = User.objects.filter(role__in=['Storekeeper', 'Manager'])
                for user in users:
                    NotificationReceipt.objects.get_or_create(
                        notification=notification,
                        user=user
                    )
    
    @receiver(post_save, sender=Ingredient)
    def check_low_stock_notification(sender, instance, **kwargs):
        """
        Create notification when ingredient crosses into low stock state.
        """
        current_is_low = instance.total_quantity <= instance.low_stock_threshold
        if not current_is_low:
            return

        previous_snapshot = getattr(instance, '_previous_stock_snapshot', None)
        if previous_snapshot:
            previous_total = previous_snapshot['total_quantity']
            previous_threshold = previous_snapshot['low_stock_threshold']
            previous_is_low = previous_total <= previous_threshold
            if previous_is_low:
                return

            notification = Notification.objects.create(
                title=f"Low Stock: {instance.name}",
                message=(
                    f"{instance.name} ({instance.total_quantity} {instance.base_unit}) "
                    f"is at or below the threshold of "
                    f"{instance.threshold_display_value} {instance.effective_threshold_unit}"
                ),
                type='LowStock',
                icon='warning'
            )
            
            # Send to Manager, Storekeeper, and Baker
            users = User.objects.filter(role__in=['Manager', 'Storekeeper', 'Baker'])
            for user in users:
                NotificationReceipt.objects.get_or_create(
                    notification=notification,
                    user=user
                )

    @receiver(pre_save, sender=Ingredient)
    def capture_previous_stock_state(sender, instance, **kwargs):
        """Store previous stock/threshold values to detect low-stock transitions."""
        if not instance.pk:
            instance._previous_stock_snapshot = None
            return

        previous = Ingredient.objects.filter(pk=instance.pk).values(
            'total_quantity',
            'low_stock_threshold',
        ).first()
        instance._previous_stock_snapshot = previous
    
    @receiver(post_save, sender=ProductWastage)
    def check_high_wastage_notification(sender, instance, created, **kwargs):
        """
        Create notification when product wastage is high (total_loss indicates it).
        Monitor for significant waste events.
        """
        if not created:
            return
        
        # Create notification for significant wastage
        if instance.total_loss > 0:
            notification = Notification.objects.create(
                title=f"Wastage Reported: {instance.product_id.name}",
                message=f"Quantity: {instance.quantity}. Loss: Rs. {instance.total_loss:.2f}. Reason: {instance.reason_id.reason}",
                type='HighWastage',
                icon='alert'
            )
            
            # Send to Manager and Baker
            users = User.objects.filter(role__in=['Manager', 'Baker'])
            for user in users:
                NotificationReceipt.objects.get_or_create(
                    notification=notification,
                    user=user
                )
    
    @receiver(post_save, sender=Product)
    def check_out_of_stock_notification(sender, instance, **kwargs):
        """
        Create notification when product goes out of stock.
        """
        if instance.current_stock == 0:
            # Check if notification already exists today
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            recent_notification = Notification.objects.filter(
                type='OutOfStock',
                title__contains=instance.name,
                created_at__gte=today_start
            ).first()
            
            if recent_notification:
                return  # Already notified today
            
            notification = Notification.objects.create(
                title=f"Out of Stock: {instance.name}",
                message=f"{instance.name} is now completely out of stock. Consider producing more if possible.",
                type='OutOfStock',
                icon='error'
            )
            
            # Send to Manager and Baker
            users = User.objects.filter(role__in=['Manager', 'Baker'])
            for user in users:
                NotificationReceipt.objects.get_or_create(
                    notification=notification,
                    user=user
                )
