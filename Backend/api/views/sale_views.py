from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count, Avg, Q, Prefetch
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from api.models import Sale, SaleItem, User
from api.serializers import SaleListSerializer, SaleDetailSerializer, SaleCreateSerializer
from api.serializers import SaleAnalyticsSerializer, CashierSalesSerializer, PaymentMethodSalesSerializer
from api.permissions import IsCashierOrManager, IsCashier, IsManager
from api.utils.query_optimization import OptimizedQueryMixin


class SalePagination(PageNumberPagination):
    """Custom pagination for sale list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SaleViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for Sale management with query optimization.
    
    Endpoints:
    - GET /api/sales/              - List all sales (paginated)
    - POST /api/sales/             - Create new sale (checkout)
    - GET /api/sales/{id}/         - Get sale details
    - GET /api/sales/active/       - Get today's sales
    - GET /api/sales/date-range/   - Get sales by date range
    - GET /api/sales/cashier/{id}/ - Get sales by cashier
    - GET /api/sales/payment-method/ - Get sales by payment method
    - GET /api/sales/analytics/    - Get sales analytics
    """
    
    queryset = Sale.objects.all()
    serializer_class = SaleListSerializer
    permission_classes = [IsCashierOrManager]
    pagination_class = SalePagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['cashier_id', 'discount_id'],
            'prefetch_related': Prefetch('items', queryset=SaleItem.objects.select_related('product_id')),
        },
        'retrieve': {
            'select_related': ['cashier_id', 'discount_id'],
            'prefetch_related': Prefetch('items', queryset=SaleItem.objects.select_related('product_id')),
        }
    }
    
    def get_serializer_class(self):
        """Route to appropriate serializer based on action"""
        if self.action == 'create':
            return SaleCreateSerializer
        elif self.action in ['retrieve', 'get_sale_details']:
            return SaleDetailSerializer
        elif self.action == 'get_analytics':
            return SaleAnalyticsSerializer
        elif self.action == 'cashier_sales':
            return CashierSalesSerializer
        elif self.action == 'payment_methods':
            return PaymentMethodSalesSerializer
        return SaleListSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [IsCashierOrManager()]  # Both Cashier and Manager can create sales
        elif self.action in ['get_analytics', 'get_detailed_analytics']:
            return [IsManager()]
        return super().get_permissions()
    
    def get_queryset(self):
        """Filter sales based on user role with optimized queries"""
        user = self.request.user
        queryset = Sale.objects.all()
        
        # Cashier can only see own sales
        if user.role == 'Cashier':
            queryset = queryset.filter(cashier_id=user)
        
        # Filter by date if provided
        start_date = self.request.query_params.get('start_date') or self.request.query_params.get('date_from')
        end_date = self.request.query_params.get('end_date') or self.request.query_params.get('date_to')
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date_time__date__gte=start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date_time__date__lte=end)
            except ValueError:
                pass
        
        # Filter by payment method if provided
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        # Search by bill number (matches Sales History PDF screen behavior).
        search = (self.request.query_params.get('search') or '').strip()
        if search:
            queryset = queryset.filter(bill_number__icontains=search)

        # Optional amount filter parity with Sales History screen.
        amount_filter = (self.request.query_params.get('amount_filter') or '').strip().lower()
        if amount_filter == 'high':
            queryset = queryset.filter(total_amount__gt=1000)
        
        # Filter by cashier if provided
        cashier_id = self.request.query_params.get('cashier_id')
        if cashier_id and self.request.user.role == 'Manager':
            queryset = queryset.filter(cashier_id=cashier_id)
        
        # Apply optimized query patterns
        return queryset.select_related('cashier_id', 'discount_id').prefetch_related(
            Prefetch('items', queryset=SaleItem.objects.select_related('product_id'))
        )
    
    def create(self, request, *args, **kwargs):
        """Create a new sale (checkout)"""
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        
        # Return detailed response
        output_serializer = SaleDetailSerializer(sale)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='active')
    def get_active_sales(self, request):
        """Get today's sales"""
        today = timezone.now().date()
        sales = self.get_queryset().filter(date_time__date=today)
        
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='date-range')
    def get_by_date_range(self, request):
        """Get sales by date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Date format must be YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sales = self.get_queryset().filter(
            date_time__date__gte=start,
            date_time__date__lte=end
        )
        
        serializer = self.get_serializer(sales, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='cashier/(?P<cashier_id>[0-9]+)')
    def cashier_sales(self, request, cashier_id=None):
        """Get sales by specific cashier (Manager only)"""
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only Manager can view other cashiers sales'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            cashier = User.objects.get(id=cashier_id, role='Cashier')
        except User.DoesNotExist:
            return Response(
                {'error': 'Cashier not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sales = Sale.objects.filter(cashier_id=cashier).prefetch_related('items')
        
        # Get summary stats
        stats = sales.aggregate(
            total_sales=Count('id'),
            total_amount=Sum('total_amount'),
            total_discount=Sum('discount_amount')
        )
        # Calculate average sale separately
        if stats['total_sales'] > 0:
            stats['average_sale'] = stats['total_amount'] / stats['total_sales']
        else:
            stats['average_sale'] = 0
        
        response_data = {
            'cashier_id': cashier.id,
            'cashier_name': cashier.full_name,
            'total_sales': stats['total_sales'] or 0,
            'total_amount': stats['total_amount'] or 0,
            'average_sale': stats['average_sale'] or 0,
            'total_discount': stats['total_discount'] or 0,
            'sales': SaleListSerializer(sales, many=True).data
        }
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'], url_path='payment-method')
    def payment_methods(self, request):
        """Get sales breakdown by payment method"""
        payment_methods = request.query_params.get('payment_method')
        
        sales = self.get_queryset()
        
        # Get breakdown by payment method
        breakdown = sales.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        ).order_by('-total_amount')
        
        response_data = list(breakdown)
        return Response(response_data)
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def get_analytics(self, request):
        """Get sales analytics (Manager only)"""
        period = request.query_params.get('period', 'today')  # today, week, month
        
        if period == 'today':
            start_date = timezone.now().date()
            end_date = start_date
        elif period == 'week':
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            return Response(
                {'error': 'period must be: today, week, or month'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sales = Sale.objects.filter(
            date_time__date__gte=start_date,
            date_time__date__lte=end_date
        )
        
        # Overall stats
        overall_stats = sales.aggregate(
            total_sales=Count('id'),
            total_amount=Sum('total_amount'),
            total_discount=Sum('discount_amount')
        )
        # Calculate average sale separately
        if overall_stats['total_sales'] > 0:
            overall_stats['average_sale'] = overall_stats['total_amount'] / overall_stats['total_sales']
        else:
            overall_stats['average_sale'] = 0
        
        # Daily breakdown
        daily_breakdown_raw = sales.values('date_time__date').annotate(
            total_sales=Count('id'),
            total_amount=Sum('total_amount'),
            total_discount=Sum('discount_amount')
        ).order_by('date_time__date')
        
        # Calculate averages for daily breakdown
        daily_breakdown = []
        for item in daily_breakdown_raw:
            if item['total_sales'] > 0:
                item['average_sale'] = item['total_amount'] / item['total_sales']
            else:
                item['average_sale'] = 0
            daily_breakdown.append(item)
        
        # Payment method breakdown
        payment_breakdown = sales.values('payment_method').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )
        
        # Cashier breakdown
        cashier_breakdown = sales.values('cashier_id', 'cashier_id__full_name').annotate(
            count=Count('id'),
            total_amount=Sum('total_amount')
        )
        
        response_data = {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'overall': {
                'total_sales': overall_stats['total_sales'] or 0,
                'total_amount': overall_stats['total_amount'] or 0,
                'average_sale': overall_stats['average_sale'] or 0,
                'total_discount': overall_stats['total_discount'] or 0,
            },
            'daily_breakdown': list(daily_breakdown),
            'payment_breakdown': list(payment_breakdown),
            'cashier_breakdown': list(cashier_breakdown),
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'], url_path='items')
    def get_sale_items(self, request, pk=None):
        """Get all items in a specific sale"""
        try:
            sale = self.get_queryset().get(id=pk)
        except Sale.DoesNotExist:
            return Response(
                {'error': 'Sale not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        items = sale.items.all()
        from api.serializers import SaleItemSerializer
        serializer = SaleItemSerializer(items, many=True)
        
        return Response({
            'bill_number': sale.bill_number,
            'items': serializer.data,
            'item_count': items.count()
        })
    
    @action(detail=False, methods=['get'], url_path='next-bill-number')
    def get_next_bill_number(self, request):
        """Get the next available bill number"""
        try:
            # Get the latest sale
            latest_sale = Sale.objects.all().order_by('-id').first()
            
            if not latest_sale or not latest_sale.bill_number:
                # No sales yet, start from 1001
                next_bill_num = 1001
            else:
                # Extract numeric part from bill_number (format: "BILL-XXXX")
                bill_str = latest_sale.bill_number
                if bill_str.startswith('BILL-'):
                    current_num = int(bill_str.replace('BILL-', ''))
                    next_bill_num = current_num + 1
                else:
                    # Fallback if format is different
                    next_bill_num = 1001
            
            # Format as "BILL-XXXX"
            next_bill_number = f"BILL-{str(next_bill_num).zfill(4)}"
            
            return Response({
                'next_bill_number': next_bill_number,
                'next_number': next_bill_num
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to get next bill number: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        """Export filtered sales history to Excel with a total revenue summary row."""
        sales = self.get_queryset().order_by('-date_time')

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
        except ImportError:
            return Response(
                {'detail': 'Excel generation dependency missing. Install openpyxl.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Sales History'

        headers = [
            'Bill Number',
            'Date & Time',
            'Cashier Name',
            'Payment Method',
            'Subtotal',
            'Discount',
            'Final Total',
        ]
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True)

        total_revenue = 0
        for sale in sales:
            cashier_name = sale.cashier_id.full_name or sale.cashier_id.username
            subtotal = float(sale.subtotal or 0)
            discount = float(sale.discount_amount or 0)
            final_total = float(sale.total_amount or 0)

            total_revenue += final_total

            sheet.append([
                sale.bill_number,
                timezone.localtime(sale.date_time).strftime('%Y-%m-%d %I:%M:%S %p'),
                cashier_name,
                sale.payment_method,
                subtotal,
                discount,
                final_total,
            ])

        summary_row_idx = sheet.max_row + 1
        sheet.append(['', '', '', '', '', 'Total Revenue', total_revenue])
        sheet[f'F{summary_row_idx}'].font = Font(bold=True)
        sheet[f'G{summary_row_idx}'].font = Font(bold=True)

        sheet.column_dimensions['A'].width = 18
        sheet.column_dimensions['B'].width = 24
        sheet.column_dimensions['C'].width = 24
        sheet.column_dimensions['D'].width = 18
        sheet.column_dimensions['E'].width = 14
        sheet.column_dimensions['F'].width = 14
        sheet.column_dimensions['G'].width = 14

        from io import BytesIO
        output = BytesIO()
        workbook.save(output)
        excel_bytes = output.getvalue()
        output.close()

        filename = f"sales_report_{timezone.localtime().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
