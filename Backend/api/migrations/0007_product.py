# Generated migration for Product model - Created manually due to circular import

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0006_ingredientbatch"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_id",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        help_text="Auto-generated: #PROD-1001, #PROD-1002, etc.",
                        max_length=50,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="e.g., 'White Bread Loaf', 'Chocolate Cake'",
                        max_length=100,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Product description for display",
                        null=True,
                    ),
                ),
                (
                    "image_url",
                    models.URLField(
                        blank=True,
                        help_text="URL to product image",
                        null=True,
                    ),
                ),
                (
                    "cost_price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Cost to produce per unit",
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.01")
                            )
                        ],
                    ),
                ),
                (
                    "selling_price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Selling price per unit",
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.01")
                            )
                        ],
                    ),
                ),
                (
                    "current_stock",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        help_text="Current quantity in stock (pieces/units)",
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0"))
                        ],
                    ),
                ),
                (
                    "shelf_life",
                    models.IntegerField(
                        default=1,
                        help_text="How long product lasts after production",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "shelf_unit",
                    models.CharField(
                        choices=[
                            ("hours", "Hours"),
                            ("days", "Days"),
                            ("weeks", "Weeks"),
                        ],
                        default="days",
                        help_text="Time unit for shelf_life",
                        max_length=20,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                    ),
                ),
                (
                    "category_id",
                    models.ForeignKey(
                        help_text="Must be a Product-type category",
                        limit_choices_to={"type": "Product"},
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="products",
                        to="api.category",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["product_id"], name="api_product_product_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["category_id", "name"], name="api_product_cat_name_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["created_at"], name="api_product_created_idx"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="product",
            unique_together={("category_id", "name")},
        ),
    ]
