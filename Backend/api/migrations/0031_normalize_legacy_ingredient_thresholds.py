from decimal import Decimal

from django.db import migrations


def normalize_legacy_thresholds(apps, schema_editor):
    Ingredient = apps.get_model('api', 'Ingredient')

    legacy_items = Ingredient.objects.filter(threshold_unit='')

    for ingredient in legacy_items.iterator():
        threshold = ingredient.low_stock_threshold or Decimal('0')

        if ingredient.tracking_type == 'Weight':
            ingredient.low_stock_threshold = threshold * Decimal('1000')
            ingredient.threshold_unit = 'kg'
        elif ingredient.tracking_type == 'Volume':
            ingredient.low_stock_threshold = threshold * Decimal('1000')
            ingredient.threshold_unit = 'L'
        else:
            ingredient.threshold_unit = 'nos'

        ingredient.save(update_fields=['low_stock_threshold', 'threshold_unit'])


def noop_reverse(apps, schema_editor):
    # This is a one-time data normalization migration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_expand_wastage_monetary_fields'),
    ]

    operations = [
        migrations.RunPython(normalize_legacy_thresholds, noop_reverse),
    ]
