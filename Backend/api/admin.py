from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    Category,
    Product,
    ProductStockHistory,
    Ingredient,
    IngredientBatch,
    IngredientStockHistory,
    ProductBatch,
    RecipeItem,
    Sale,
    SaleItem,
    Discount,
    Notification,
    NotificationReceipt,
    WastageReason,
    ProductWastage,
    IngredientWastage,
)


# ============================================================
# USER ADMIN
# ============================================================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin for BakeryOS"""
    
    list_display = (
        'username',
        'full_name',
        'employee_id',
        'role',
        'is_active',
        'date_joined',
    )
    
    list_filter = (
        'role',
        'is_active',
        'date_joined',
    )
    
    search_fields = (
        'username',
        'full_name',
        'employee_id',
        'email',
    )
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('BakeryOS Custom Fields', {
            'fields': (
                'employee_id',
                'full_name',
                'nic',
                'contact',
                'role',
                'avatar_color',
            ),
        }),
    )


# ============================================================
# CATEGORY ADMIN
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    list_display = (
        'category_id',
        'name',
        'type',
        'created_at',
    )
    
    list_filter = (
        'type',
        'created_at',
    )
    
    search_fields = (
        'name',
        'category_id',
    )
    
    readonly_fields = (
        'category_id',
        'created_at',
    )


# ============================================================
# PRODUCT ADMIN
# ============================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = (
        'product_id',
        'name',
        'category_id',
        'selling_price',
        'cost_price',
        'current_stock',
    )
    
    list_filter = (
        'category_id',
        'created_at',
    )
    
    search_fields = (
        'product_id',
        'name',
    )
    
    fieldsets = (
        ('Product Information', {
            'fields': (
                'name',
                'category_id',
                'description',
                'image_url',
            ),
        }),
        ('Pricing & Stock', {
            'fields': (
                'selling_price',
                'cost_price',
                'current_stock',
            ),
        }),
        ('Shelf Life', {
            'fields': (
                'shelf_life',
                'shelf_unit',
            ),
        }),
        ('Metadata', {
            'fields': (
                'product_id',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'product_id',
        'created_at',
        'updated_at',
    )


@admin.register(ProductStockHistory)
class ProductStockHistoryAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'product_id',
        'created_at',
    )
    
    list_filter = (
        'created_at',
    )
    
    search_fields = (
        'product_id__name',
    )
    
    readonly_fields = (
        'product_id',
        'created_at',
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# INGREDIENT ADMIN
# ============================================================

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    
    list_display = (
        'ingredient_id',
        'name',
        'category_id',
        'supplier',
    )
    
    list_filter = (
        'category_id',
        'created_at',
    )
    
    search_fields = (
        'ingredient_id',
        'name',
        'supplier',
    )
    
    fieldsets = (
        ('Ingredient Information', {
            'fields': (
                'name',
                'category_id',
                'description',
            ),
        }),
        ('Stock Management', {
            'fields': (
                'quantity',
                'reorder_level',
            ),
        }),
        ('Supplier Information', {
            'fields': (
                'supplier',
                'supplier_contact',
                'cost_per_unit',
            ),
        }),
        ('Metadata', {
            'fields': (
                'ingredient_id',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'ingredient_id',
        'created_at',
    )


# ============================================================
# BATCH ADMIN
# ============================================================

@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    
    list_display = (
        'batch_id',
        'product_id',
        'quantity',
        'status',
    )
    
    list_filter = (
        'product_id',
        'status',
    )
    
    search_fields = (
        'batch_id',
        'product_id__name',
    )
    
    fieldsets = (
        ('Batch Information', {
            'fields': (
                'batch_id',
                'product_id',
            ),
        }),
        ('Batch Details', {
            'fields': (
                'quantity',
                'made_date',
                'expire_date',
                'status',
            ),
        }),
        ('Notes', {
            'fields': (
                'notes',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'batch_id',
        'created_at',
        'updated_at',
    )


@admin.register(IngredientBatch)
class IngredientBatchAdmin(admin.ModelAdmin):
    
    list_display = (
        'batch_id',
        'ingredient_id',
        'quantity',
        'status',
    )
    
    list_filter = (
        'ingredient_id',
    )
    
    search_fields = (
        'batch_id',
        'ingredient_id__name',
    )
    
    fieldsets = (
        ('Batch Information', {
            'fields': (
                'batch_id',
                'ingredient_id',
            ),
        }),
        ('Batch Details', {
            'fields': (
                'quantity',
                'current_qty',
                'made_date',
                'expire_date',
                'status',
            ),
        }),
        ('Cost Tracking', {
            'fields': (
                'cost_price',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'batch_id',
        'created_at',
    )


# ============================================================
# RECIPE ADMIN
# ============================================================

@admin.register(RecipeItem)
class RecipeItemAdmin(admin.ModelAdmin):
    
    list_display = (
        'product_id',
        'ingredient_id',
        'quantity_required',
    )
    
    list_filter = (
        'product_id',
    )
    
    search_fields = (
        'product_id__name',
        'ingredient_id__name',
    )


# ============================================================
# SALE ADMIN
# ============================================================

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = (
        'product_id',
        'unit_price',
        'subtotal',
    )
    fields = (
        'product_id',
        'quantity',
        'unit_price',
        'subtotal',
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    
    list_display = (
        'bill_number',
        'cashier_id',
        'total_amount',
        'payment_method',
        'date_time',
    )
    
    list_filter = (
        'payment_method',
        'date_time',
    )
    
    search_fields = (
        'bill_number',
        'cashier_id__username',
    )
    
    fieldsets = (
        ('Sale Information', {
            'fields': (
                'bill_number',
                'cashier_id',
                'date_time',
            ),
        }),
        ('Pricing', {
            'fields': (
                'subtotal',
                'discount_id',
                'discount_amount',
                'total_amount',
            ),
        }),
        ('Payment', {
            'fields': (
                'payment_method',
            ),
        }),
    )
    
    readonly_fields = (
        'bill_number',
        'subtotal',
        'discount_amount',
        'total_amount',
    )
    
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    
    list_display = (
        'sale_id',
        'product_id',
        'quantity',
        'unit_price',
    )
    
    list_filter = (
        'sale_id__date_time',
    )
    
    search_fields = (
        'sale_id__bill_number',
        'product_id__name',
    )
    
    readonly_fields = (
        'subtotal',
    )


# ============================================================
# DISCOUNT ADMIN
# ============================================================

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    
    list_display = (
        'discount_id',
        'name',
        'created_at',
    )
    
    list_filter = (
        'created_at',
    )
    
    search_fields = (
        'discount_id',
        'name',
    )
    
    fieldsets = (
        ('Discount Information', {
            'fields': (
                'name',
                'description',
            ),
        }),
        ('Discount Details', {
            'fields': (
                'kind',
                'percentage',
                'fixed_amount',
            ),
        }),
        ('Applicability', {
            'fields': (
                'target_category_id',
                'target_product_id',
            ),
        }),
        ('Dates', {
            'fields': (
                'start_date',
                'end_date',
            ),
        }),
        ('Metadata', {
            'fields': (
                'discount_id',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'discount_id',
        'created_at',
    )


# ============================================================
# NOTIFICATION ADMIN
# ============================================================

class NotificationReceiptInline(admin.TabularInline):
    model = NotificationReceipt
    extra = 0
    readonly_fields = (
        'user',
    )
    fields = (
        'user',
        'is_read',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'title',
        'type',
        'created_at',
    )
    
    list_filter = (
        'type',
        'created_at',
    )
    
    search_fields = (
        'title',
        'message',
    )
    
    fieldsets = (
        ('Notification Content', {
            'fields': (
                'title',
                'message',
                'type',
            ),
        }),
        ('Target Audience', {
            'fields': (
                'target_role',
            ),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'created_at',
    )
    
    inlines = [NotificationReceiptInline]


@admin.register(NotificationReceipt)
class NotificationReceiptAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'notification',
        'user',
        'is_read',
    )
    
    list_filter = (
        'is_read',
    )
    
    search_fields = (
        'notification__title',
        'user__username',
    )
    
    readonly_fields = (
        'notification',
        'user',
    )


# ============================================================
# WASTAGE ADMIN
# ============================================================

@admin.register(WastageReason)
class WastageReasonAdmin(admin.ModelAdmin):
    
    list_display = (
        'reason_id',
        'description',
    )
    
    search_fields = (
        'reason_id',
        'description',
    )
    
    readonly_fields = (
        'reason_id',
    )


@admin.register(ProductWastage)
class ProductWastageAdmin(admin.ModelAdmin):
    
    list_display = (
        'wastage_id',
        'product_id',
        'reason_id',
    )
    
    list_filter = (
        'reason_id',
        'created_at',
    )
    
    search_fields = (
        'wastage_id',
        'product_id__name',
    )
    
    fieldsets = (
        ('Wastage Information', {
            'fields': (
                'product_id',
                'quantity',
                'reason_id',
            ),
        }),
        ('Details', {
            'fields': (
                'unit_cost',
                'total_loss',
                'notes',
                'reported_by',
            ),
        }),
        ('Metadata', {
            'fields': (
                'wastage_id',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'wastage_id',
        'created_at',
    )


@admin.register(IngredientWastage)
class IngredientWastageAdmin(admin.ModelAdmin):
    
    list_display = (
        'wastage_id',
        'ingredient_id',
        'reason_id',
    )
    
    list_filter = (
        'reason_id',
        'created_at',
    )
    
    search_fields = (
        'wastage_id',
        'ingredient_id__name',
    )
    
    fieldsets = (
        ('Wastage Information', {
            'fields': (
                'ingredient_id',
                'batch_id',
                'quantity',
                'reason_id',
            ),
        }),
        ('Details', {
            'fields': (
                'unit_cost',
                'total_loss',
                'notes',
                'reported_by',
            ),
        }),
        ('Metadata', {
            'fields': (
                'wastage_id',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'wastage_id',
        'created_at',
    )

