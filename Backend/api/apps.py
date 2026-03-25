from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    
    def ready(self):
        """Import signals when the app is ready"""
        from . import signals  # noqa
        # Setup product signals (deferred loading)
        signals.setup_product_signals()
        # Setup stock history signals for audit trail
        signals.setup_stock_history_signals()
        # Setup notification signals
        signals.setup_notification_signals()
