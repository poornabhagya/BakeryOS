import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Reset admin password to admin@123
admin = User.objects.get(username='admin')
admin.set_password('admin@123')
admin.save()
print(f"✅ Admin password updated to 'admin@123'")
