from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_rename_api_counter_is_acti_f3b4bb_idx_api_counter_is_acti_49e9e9_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='threshold_unit',
            field=models.CharField(
                blank=True,
                choices=[
                    ('g', 'Grams (g)'),
                    ('kg', 'Kilograms (kg)'),
                    ('ml', 'Milliliters (ml)'),
                    ('L', 'Liters (L)'),
                    ('nos', 'Numbers (nos)'),
                ],
                default='',
                help_text='User-preferred unit for low stock threshold display/input',
                max_length=10,
            ),
        ),
    ]
