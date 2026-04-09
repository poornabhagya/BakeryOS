from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO
from rest_framework.pagination import PageNumberPagination
from django.db.models import F, Q
from django.utils import timezone
from datetime import timedelta
# from django_filters.rest_framework import DjangoFilterBackend  # Disabled due to compatibility
from rest_framework.filters import SearchFilter, OrderingFilter

from api.models import IngredientBatch, Ingredient, Product, Notification, NotificationReceipt, User
from api.serializers import (
    BatchListSerializer,
    BatchDetailSerializer,
    BatchCreateSerializer,
    BatchConsumeSerializer,
)
from api.permissions import IsManager, IsManagerOrStorekeeper, IsManagerOrStorekeeperOrBaker
from api.utils.query_optimization import OptimizedQueryMixin


class BatchPagination(PageNumberPagination):
    """Custom pagination for batch list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BatchViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for IngredientBatch management with query optimization.
    
    Features:
    - Auto-generated batch_id (BATCH-1001, BATCH-1002, etc.)
    - Quantity tracking with FIFO ordering
    - Expiry date management and alerts
    - Cost tracking for financial reporting
    - Automatic ingredient total_quantity sync
    - Query optimized with select_related/prefetch_related
    - Pagination on list endpoints
    
    Endpoints:
    - GET    /api/batches/                  List all batches (paginated, filtered)
    - POST   /api/batches/                  Create new batch
    - GET    /api/batches/{id}/             Get batch details
    - PUT    /api/batches/{id}/             Full update
    - PATCH  /api/batches/{id}/             Partial update
    - DELETE /api/batches/{id}/             Delete batch
    
    Custom Actions:
    - GET    /api/batches/expiring/         Get batches expiring within 2 days
    - GET    /api/batches/{id}/consume/     Consume from batch (FIFO)
    - GET    /api/ingredients/{id}/batches/ Get all active batches for ingredient (FIFO)
    
    Filtering:
    - ?ingredient_id=1         Filter by ingredient
    - ?status=Active           Filter by status (Active, Expired, Used)
    - ?expiring_within=7       Batches expiring within N days
    - ?search=BATCH-1001       Search by batch_id or ingredient name
    - ?ordering=expire_date    Sort by field
    
    Permissions:
    - Storekeeper: Full CRUD (create, update, delete)
    - Manager: Full access (can do everything)
    - Baker: Read-only (list, detail)
    - Cashier & Others: No access
    """
    
    queryset = IngredientBatch.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = BatchPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['ingredient_id'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['ingredient_id'],
            'prefetch_related': ['stock_history'],
        },
        'expiring': {
            'select_related': ['ingredient_id'],
            'prefetch_related': [],
        }
    }
    filterset_fields = ['ingredient_id', 'status']
    search_fields = ['batch_id', 'ingredient_id__name']
    ordering_fields = ['made_date', 'expire_date', 'current_qty', 'status', 'created_at']
    ordering = ['expire_date', 'made_date']  # FIFO ordering
    pagination_class = None  # No pagination for batches
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BatchListSerializer
        elif self.action == 'create':
            return BatchCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BatchCreateSerializer
        elif self.action == 'consume':
            return BatchConsumeSerializer
        else:  # retrieve, custom actions
            return BatchDetailSerializer
    
    def get_permissions(self):
        """
        Return appropriate permission classes based on action.
        
        Permissions:
        - list/retrieve: Storekeeper OR Manager OR Baker (read-only)
        - create/update/delete: Storekeeper OR Manager (write operations)
        - consume: Storekeeper OR Manager (for stock deduction)
        """
        if self.action == 'run_expiry_check':
            self.permission_classes = [IsManager]
        elif self.action in ['list', 'retrieve', 'by_ingredient', 'expiring', 'export_excel']:
            # All authenticated users can view batches
            self.permission_classes = [IsManagerOrStorekeeperOrBaker]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'consume']:
            # Only Storekeeper and Manager can modify
            self.permission_classes = [IsManagerOrStorekeeper]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """Return filtered queryset for list and related actions."""
        queryset = super().get_queryset()

        ingredient_id = self.request.query_params.get('ingredient_id')
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset

    def _create_system_audit_notification(self, message: str):
        """Create system-wide audit notification and unread receipts for active users."""
        notification = Notification.objects.create(
            title='System Audit Trail',
            message=message,
            type='System',
            icon='info'
        )

        active_users = User.objects.filter(
            is_active=True,
            role__in=['Manager', 'Cashier', 'Baker', 'Storekeeper']
        )

        NotificationReceipt.objects.bulk_create([
            NotificationReceipt(notification=notification, user=user, status='unread', is_read=False)
            for user in active_users
        ])
    
    def perform_create(self, serializer):
        """Create new ingredient batch and emit system-wide audit notification."""
        serializer.save()
        batch = serializer.instance
        message = f"{self.request.user.username} added new stock: {batch.quantity} of {batch.ingredient_id.name}"
        self._create_system_audit_notification(message)
    
    def perform_update(self, serializer):
        """Update ingredient batch and emit system-wide audit notification."""
        serializer.save()
        batch = serializer.instance
        message = f"{self.request.user.username} updated stock batch: {batch.quantity} of {batch.ingredient_id.name}"
        self._create_system_audit_notification(message)
    
    def perform_destroy(self, instance):
        """Delete ingredient batch and emit system-wide audit notification."""
        ingredient_name = instance.ingredient_id.name
        quantity = instance.quantity
        instance.delete()
        message = f"{self.request.user.username} deleted stock batch: {quantity} of {ingredient_name}"
        self._create_system_audit_notification(message)
    
    @action(detail=False, methods=['get'], url_path='expiring')
    def expiring(self, request):
        """
        Get batches expiring within specified number of days.
        
        Query Parameters:
        - days: Number of days to check (default: 2)
        
        Example:
        - GET /api/batches/expiring/?days=7
        """
        days_param = request.query_params.get('days', 2)
        try:
            days = int(days_param)
        except (ValueError, TypeError):
            days = 2
        
        expiry_date_threshold = timezone.now() + timedelta(days=days)
        
        batches = self.queryset.filter(
            status='Active',
            expire_date__lte=expiry_date_threshold,
            expire_date__gt=timezone.now()
        ).order_by('expire_date')
        
        serializer = self.get_serializer(batches, many=True)
        return Response({
            'count': batches.count(),
            'expiring_within_days': days,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='expired')
    def expired(self, request):
        """
        Get all expired batches.
        
        Example:
        - GET /api/batches/expired/
        """
        expired_batches = self.queryset.filter(
            Q(status='Expired') | Q(expire_date__lt=timezone.now())
        ).order_by('-expire_date')
        
        serializer = self.get_serializer(expired_batches, many=True)
        return Response({
            'count': expired_batches.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='out-of-stock')
    def out_of_stock(self, request):
        """
        Get batches that are fully consumed (current_qty == 0).
        
        Example:
        - GET /api/batches/out-of-stock/
        """
        empty_batches = self.queryset.filter(current_qty=0).order_by('-updated_at')
        
        serializer = self.get_serializer(empty_batches, many=True)
        return Response({
            'count': empty_batches.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='consume')
    def consume(self, request, pk=None):
        """
        Consume (use) a quantity from this batch.
        
        Request body:
        {
            "amount": 25.50
        }
        
        Returns:
        {
            "success": true,
            "message": "Consumed 25.50 from batch",
            "remaining": 74.50,
            "batch_id": "BATCH-1001"
        }
        
        Example:
        - POST /api/batches/1/consume/
          Body: {"amount": 10}
        """
        batch = self.get_object()
        serializer = BatchConsumeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        result = batch.consume(amount)
        
        if result['success']:
            # Return updated batch details
            updated_serializer = BatchDetailSerializer(batch)
            return Response({
                'message': result['message'],
                'batch': updated_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='by-ingredient/(?P<ingredient_id>[0-9]+)')
    def by_ingredient(self, request, ingredient_id=None):
        """
        Get all active batches for a specific ingredient (FIFO order).
        
        Example:
        - GET /api/batches/by-ingredient/1/
        
        Returns batches ordered by expiry date (oldest first) for FIFO consumption.
        """
        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            return Response(
                {'error': f'Ingredient #{ingredient_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        batches = self.queryset.filter(
            ingredient_id=ingredient,
            status='Active',
            current_qty__gt=0
        ).order_by('expire_date')
        
        serializer = self.get_serializer(batches, many=True)
        return Response({
            'ingredient_id': ingredient.id,
            'ingredient_name': ingredient.name,
            'count': batches.count(),
            'total_available': ingredient.total_quantity,
            'results': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='run-expiry-check')
    def run_expiry_check(self, request):
        """Run the process_expirations management command on demand (manager-only)."""
        # Extra guard for Django admin/superuser accounts.
        if request.user.role != 'Manager' and not request.user.is_superuser:
            return Response(
                {'detail': 'Only Manager or Admin can run expiry check.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        out = StringIO()
        call_command('process_expirations', stdout=out)
        message = out.getvalue().strip()

        return Response(
            {
                'detail': 'Success',
                'message': message or 'Expiry check completed successfully.',
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        """Export current stock (products + ingredients) to Excel."""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
        except ImportError:
            return Response(
                {'detail': 'Excel generation dependency missing. Install openpyxl.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        products = Product.objects.select_related('category_id').order_by('name')
        ingredients = Ingredient.objects.select_related('category_id').prefetch_related('batches').order_by('name')

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Current Stock'

        headers = ['Item ID', 'Item Name', 'Item Type', 'Category', 'Price (Rs)', 'Cost (Rs)', 'Quantity']
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        total_price = 0.0
        total_cost = 0.0

        for product in products:
            price_value = float(product.selling_price or 0)
            cost_value = float(product.cost_price or 0)
            total_price += price_value
            total_cost += cost_value
            sheet.append([
                product.product_id,
                product.name,
                'Product',
                product.category_id.name if product.category_id else 'N/A',
                price_value,
                cost_value,
                float(product.current_stock or 0),
            ])

        for ingredient in ingredients:
            latest_batch = ingredient.batches.filter(total_batch_cost__isnull=False).order_by('-created_at').first()
            ingredient_cost = float(latest_batch.total_batch_cost) if latest_batch and latest_batch.total_batch_cost is not None else 0.0
            total_cost += ingredient_cost
            sheet.append([
                ingredient.ingredient_id,
                ingredient.name,
                'Ingredient',
                ingredient.category_id.name if ingredient.category_id else 'N/A',
                None,
                ingredient_cost,
                float(ingredient.total_quantity or 0),
            ])

        summary_row_idx = sheet.max_row + 1
        sheet.append(['', '', '', 'TOTAL', total_price, total_cost, ''])
        sheet[f'D{summary_row_idx}'].font = Font(bold=True)
        sheet[f'E{summary_row_idx}'].font = Font(bold=True)
        sheet[f'F{summary_row_idx}'].font = Font(bold=True)

        sheet.column_dimensions['A'].width = 16
        sheet.column_dimensions['B'].width = 28
        sheet.column_dimensions['C'].width = 14
        sheet.column_dimensions['D'].width = 20
        sheet.column_dimensions['E'].width = 14
        sheet.column_dimensions['F'].width = 14
        sheet.column_dimensions['G'].width = 12

        from io import BytesIO
        output = BytesIO()
        workbook.save(output)
        excel_bytes = output.getvalue()
        output.close()

        filename = f"current_stock_report_{timezone.localtime().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
