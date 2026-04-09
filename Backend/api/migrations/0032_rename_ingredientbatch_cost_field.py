from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_normalize_legacy_ingredient_thresholds'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientbatch',
            old_name='cost_price',
            new_name='total_batch_cost',
        ),
    ]
