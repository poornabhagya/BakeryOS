import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Get or create admin and reset password
admin = User.objects.get(username='admin')
admin.set_password('password')
admin.save()
print(f"✅ Admin password reset to 'password'")
