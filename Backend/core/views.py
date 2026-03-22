from django.views.generic import RedirectView
from django.urls import reverse_lazy

class RedirectToAdminView(RedirectView):
    """Redirect root URL to admin panel or API docs"""
    url = '/admin/'
    permanent = False
