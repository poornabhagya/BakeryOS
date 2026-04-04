from django.db import models
from django.utils import timezone


class CounterSession(models.Model):
    """Tracks one open/close counter session for shift summary reporting."""

    opened_at = models.DateTimeField(default=timezone.now, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    opened_by = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='opened_counter_sessions',
    )
    closed_by = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='closed_counter_sessions',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['is_active', 'opened_at']),
            models.Index(fields=['opened_by', 'opened_at']),
        ]

    def __str__(self):
        status = 'Active' if self.is_active else 'Closed'
        return f"CounterSession #{self.id} ({status})"
