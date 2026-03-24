import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User

# Delete and recreate test users with correct roles
usernames_to_delete = ['baker1', 'manager1', 'storekeeper1', 'cashier1']

for username in usernames_to_delete:
    User.objects.filter(username=username).delete()
    print(f"Deleted user: {username}")

# Create test users with correct roles
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
    
    user = User.objects.create_user(
        username=username,
        password=password,
        role=role
    )
    
    print(f"✓ Created user: {username} (role: {user.role})")

print("\nAll test users ready with correct roles!")

# Verify
print("\nVerification:")
for username in ['baker1', 'manager1', 'storekeeper1', 'cashier1']:
    user = User.objects.get(username=username)
    print(f"  {username}: role='{user.role}'")
