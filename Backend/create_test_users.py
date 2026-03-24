import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User

# Create test users if they don't exist
users_to_create = [
    {'username': 'baker1', 'password': 'baker123', 'role': 'Baker'},
    {'username': 'manager1', 'password': 'manager123', 'role': 'Manager'},
    {'username': 'storekeeper1', 'password': 'storekeeper123', 'role': 'Storekeeper'},
    {'username': 'cashier1', 'password': 'cashier123', 'role': 'Cashier'},
]

for user_data in users_to_create:
    username = user_data['username']
    password = user_data['password']
    role = user_data['role']
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'role': role}
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created user: {username} ({role})")
    else:
        # Update password if user exists
        user.set_password(password)
        user.save()
        print(f"✓ Updated user: {username} ({role})")

print("\nAll test users ready!")
