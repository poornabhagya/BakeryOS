import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date
from api.models import User, Category, Product

# Create users with different roles
baker = User.objects.get_or_create(
    username='baker_test_2',
    defaults={'password': 'testpass123', 'role': 'baker'}
)[0]

category, _ = Category.objects.get_or_create(
    name='Bread Test',
    type='Product',
    defaults={'description': 'Bread products'}
)

product, _ = Product.objects.get_or_create(
    name='Sourdough Bread Test',
    defaults={
        'category_id': category,
        'cost_price': Decimal('2.50'),
        'selling_price': Decimal('5.00'),
        'shelf_life': 2,
        'shelf_unit': 'days',
        'current_stock': Decimal('0.00')
    }
)

client = APIClient()
client.force_authenticate(user=baker)

payload = {
    'product_id': product.id,
    'quantity': '10',
    'made_date': date.today().isoformat()
}

response = client.post('/api/product-batches/', payload, format='json')
print(f"Status: {response.status_code}")
print(f"Response: {response.data}")

