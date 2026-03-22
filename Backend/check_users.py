import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Check if admin exists
try:
    admin = User.objects.get(username='admin')
    print(f"✅ Admin user exists: {admin.full_name}, is_active={admin.is_active}")
except User.DoesNotExist:
    print("❌ Admin user doesn't exist. Creating...")
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
    print(f"✅ Admin created: {admin.full_name}")

# List all users
users = User.objects.all()
print(f"\n📋 Total users: {users.count()}")
for user in users:
    print(f"  - {user.username} ({user.role}) is_active={user.is_active}")
