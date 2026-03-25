from django.db import models


class WastageReason(models.Model):
    """
    Model to track reasons for product/ingredient wastage.
    Provides predefined categories for wastage reporting.
    """

    # Primary key
    id = models.AutoField(primary_key=True)

    # Auto-generated identifier
    reason_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )  # Format: WR-001, WR-002, etc.

    # Core fields
    reason = models.CharField(
        max_length=100,
        unique=True
    )  # e.g., "Expired", "Damaged", "Spilled", etc.

    description = models.TextField(
        blank=True,
        null=True
    )  # e.g., "Products past expiry date"

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reason_id']
        indexes = [
            models.Index(fields=['reason_id']),
            models.Index(fields=['reason']),
        ]

    def __str__(self):
        return f"{self.reason_id} - {self.reason}"

    def save(self, *args, **kwargs):
        """Auto-generate reason_id before saving"""
        if not self.reason_id:
            # Count existing reasons
            last_reason = WastageReason.objects.order_by('-id').first()

            if last_reason and last_reason.reason_id:
                # Extract number from last WR-001
                last_num = int(last_reason.reason_id.split('-')[1])
                # Increment and format
                new_num = str(last_num + 1).zfill(3)
            else:
                # First reason
                new_num = '001'

            self.reason_id = f'WR-{new_num}'

        super().save(*args, **kwargs)
