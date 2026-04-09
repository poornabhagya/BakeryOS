from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_ingredient_threshold_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientwastage',
            name='unit_cost',
            field=models.DecimalField(decimal_places=2, help_text='Cost per unit at time of wastage', max_digits=15),
        ),
        migrations.AlterField(
            model_name='ingredientwastage',
            name='total_loss',
            field=models.DecimalField(decimal_places=2, editable=False, help_text='Calculated as quantity * unit_cost', max_digits=15),
        ),
        migrations.AlterField(
            model_name='productwastage',
            name='unit_cost',
            field=models.DecimalField(decimal_places=2, help_text='Cost per unit at time of wastage', max_digits=15),
        ),
        migrations.AlterField(
            model_name='productwastage',
            name='total_loss',
            field=models.DecimalField(decimal_places=2, editable=False, help_text='Calculated as quantity * unit_cost', max_digits=15),
        ),
    ]
