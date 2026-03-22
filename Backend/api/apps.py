from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'
    
    def ready(self):
        """Import signals when the app is ready"""
        from . import signals  # noqa
