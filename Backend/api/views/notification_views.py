from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone
from io import BytesIO
from decimal import Decimal

from api.models import CounterSession, Notification, NotificationReceipt, Sale, User
from api.serializers import (
    NotificationListSerializer,
    NotificationDetailSerializer,
    NotificationReceiptSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
)
from api.utils.query_optimization import OptimizedQueryMixin
from api.utils.counter_notifications import create_counter_status_notification


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for notifications with query optimization.
    
    Endpoints:
    - GET /api/notifications/ - List my notifications (paginated)
    - GET /api/notifications/{id}/ - Get notification details
    - DELETE /api/notifications/{id}/ - Delete notification
    - PATCH /api/notifications/{id}/read/ - Mark as read
    - PATCH /api/notifications/read-all/ - Mark all as read
    - GET /api/notifications/unread/count/ - Get unread count
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': [],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': [],
            'prefetch_related': [],
        }
    }

    def _user_is_manager(self, user):
        return (
            user.groups.filter(name='Manager').exists()
            or user.role == 'Manager'
            or user.is_superuser
        )

    def _get_counter_notification_for_user(self, user, notification_id):
        return Notification.objects.filter(
            id=notification_id,
            title='Counter Status Update',
            type='System',
            receipts__user=user,
        ).first()

    def _get_counter_session_for_notification(self, notification):
        session = notification.counter_session
        if session is None:
            # Fallback for legacy records created before counter_session linkage existed.
            session = CounterSession.objects.filter(
                closed_at__isnull=False,
                closed_at__lte=notification.created_at,
            ).order_by('-closed_at').first()
        return session

    def _get_shift_sales_summary(self, session):
        sales = Sale.objects.filter(date_time__gte=session.opened_at, date_time__lte=session.closed_at)
        total_amount = sales.aggregate(total=Coalesce(Sum('total_amount'), Decimal('0')))['total']
        total_transactions = sales.count()
        cash_sales = sales.filter(payment_method='Cash').aggregate(total=Coalesce(Sum('total_amount'), Decimal('0')))['total']
        card_sales = sales.filter(payment_method='Card').aggregate(total=Coalesce(Sum('total_amount'), Decimal('0')))['total']
        return {
            'total_amount': total_amount,
            'total_transactions': total_transactions,
            'cash_sales': cash_sales,
            'card_sales': card_sales,
        }

    def _mark_notification_as_read_for_user(self, notification, user):
        receipt = NotificationReceipt.objects.filter(notification=notification, user=user).first()
        if receipt is None:
            return
        receipt.is_read = True
        receipt.status = 'read'
        receipt.read_at = timezone.now()
        receipt.snooze_until = None
        receipt.save(update_fields=['is_read', 'status', 'read_at', 'snooze_until'])
    
    def get_queryset(self):
        """Get notifications for current user"""
        user = self.request.user
        now = timezone.now()
        active_receipts = NotificationReceipt.objects.filter(
            user=user
        ).filter(
            Q(snooze_until__isnull=True) | Q(snooze_until__lte=now)
        )

        # Get all notifications where user has an active (not currently snoozed) receipt
        return Notification.objects.filter(
            receipts__in=active_receipts
        ).select_related().distinct().order_by('-created_at')
    
    def get_serializer_class(self):
        """Choose serializer based on action"""
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'retrieve':
            return NotificationDetailSerializer
        elif self.action == 'create':
            return NotificationCreateSerializer
        return NotificationListSerializer
    
    def list(self, request, *args, **kwargs):
        """List all notifications for current user"""
        # Mark all as viewed (but not necessarily read)
        queryset = self.get_queryset()
        
        # Apply filters
        is_read = request.query_params.get('is_read')
        notification_type = request.query_params.get('type')
        
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(receipts__user=request.user, receipts__is_read=is_read_bool)
        
        if notification_type:
            queryset = queryset.filter(type=notification_type)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Get notification details and mark as read"""
        notification = self.get_object()
        
        # Mark as read for this user
        try:
            receipt = NotificationReceipt.objects.get(
                notification=notification,
                user=request.user
            )
            receipt.mark_as_read()
        except NotificationReceipt.DoesNotExist:
            pass
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete notification for user (soft delete via receipt removal)"""
        notification = self.get_object()
        
        # Remove receipt for this user
        NotificationReceipt.objects.filter(
            notification=notification,
            user=request.user
        ).delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests to update notification status.
        Sets the status (unread/read/snoozed/archived) for the current user's receipt.
        """
        notification = self.get_object()
        status_value = request.data.get('status')
        
        if status_value not in ['unread', 'read', 'snoozed', 'archived']:
            return Response(
                {'detail': f'Invalid status. Must be one of: unread, read, snoozed, archived'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            receipt = NotificationReceipt.objects.get(
                notification=notification,
                user=request.user
            )
            
            # Update status
            receipt.status = status_value
            
            # If status is 'read', also update is_read and read_at
            if status_value == 'read':
                receipt.is_read = True
                receipt.read_at = timezone.now()
                receipt.snooze_until = None
            elif status_value == 'unread':
                receipt.is_read = False
                receipt.read_at = None
                receipt.snooze_until = None
            elif status_value == 'snoozed':
                receipt.snooze_until = timezone.now() + timedelta(hours=1)
            elif status_value == 'archived':
                receipt.snooze_until = None
            
            receipt.save(update_fields=['status', 'is_read', 'read_at', 'snooze_until'])
            
            # Return updated notification
            serializer = self.get_serializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except NotificationReceipt.DoesNotExist:
            return Response(
                {'detail': 'Notification receipt not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    
    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        """Mark a specific notification as read"""
        notification = self.get_object()
        
        try:
            receipt = NotificationReceipt.objects.get(
                notification=notification,
                user=request.user
            )
            receipt.mark_as_read()
            return Response(
                {'detail': 'Notification marked as read'},
                status=status.HTTP_200_OK
            )
        except NotificationReceipt.DoesNotExist:
            return Response(
                {'detail': 'Notification receipt not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['patch'])
    def read_all(self, request):
        """Mark all notifications as read for current user"""
        receipts = NotificationReceipt.objects.filter(
            user=request.user,
            is_read=False
        )
        
        count = receipts.count()
        
        # Mark all as read
        for receipt in receipts:
            receipt.mark_as_read()
        
        return Response(
            {'detail': f'{count} notifications marked as read'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread count for current user"""
        unread_count = NotificationReceipt.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        total_count = NotificationReceipt.objects.filter(
            user=request.user
        ).count()
        
        read_count = total_count - unread_count
        
        serializer = NotificationStatsSerializer({
            'total': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
        })
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get notifications filtered by type"""
        notification_type = request.query_params.get('type')
        
        if not notification_type:
            return Response(
                {'detail': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(type=notification_type)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all notifications for current user"""
        count = NotificationReceipt.objects.filter(
            user=request.user
        ).delete()[0]
        
        return Response(
            {'detail': f'{count} notifications cleared'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='counter-status')
    def counter_status(self, request):
        """Broadcast counter open/close system notifications to manager/cashier users."""
        if request.user.role not in ['Manager', 'Cashier']:
            return Response(
                {'detail': 'Only Manager or Cashier can trigger counter status notifications.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        action_value = request.data.get('action')
        if action_value not in ['opened', 'closed']:
            return Response(
                {'detail': "Invalid action. Expected 'opened' or 'closed'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            notification = create_counter_status_notification(
                actor=request.user,
                action=action_value,
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'detail': 'Counter status notification created successfully.',
                'notification_id': notification.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['get'], url_path='counter-report-pdf/(?P<notification_id>[^/.]+)')
    def counter_report_pdf(self, request, notification_id=None):
        """Generate and download a shift summary PDF for a counter status notification."""
        if not self._user_is_manager(request.user):
            return Response(
                {'detail': 'Detailed reports are only available for Managers.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification = self._get_counter_notification_for_user(request.user, notification_id)

        if notification is None:
            return Response({'detail': 'Counter status notification not found.'}, status=status.HTTP_404_NOT_FOUND)

        session = self._get_counter_session_for_notification(notification)

        if session is None or session.closed_at is None:
            return Response({'detail': 'No closed counter session is associated with this notification.'}, status=status.HTTP_400_BAD_REQUEST)

        summary = self._get_shift_sales_summary(session)

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            return Response(
                {'detail': 'PDF generation dependency missing. Install reportlab.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        opened_text = timezone.localtime(session.opened_at).strftime('%Y-%m-%d %I:%M %p')
        closed_text = timezone.localtime(session.closed_at).strftime('%Y-%m-%d %I:%M %p')
        opened_by = session.opened_by.full_name or session.opened_by.username
        closed_by = session.closed_by.full_name if session.closed_by and session.closed_by.full_name else (session.closed_by.username if session.closed_by else 'System')

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 56
        pdf.setFont('Helvetica-Bold', 18)
        pdf.drawString(50, y, 'BakeryOS - Shift Summary Report')

        y -= 26
        pdf.setFont('Helvetica', 11)
        pdf.drawString(50, y, f'Report Generated: {timezone.localtime().strftime("%Y-%m-%d %I:%M %p")}')

        y -= 22
        pdf.line(50, y, width - 50, y)

        y -= 24
        pdf.setFont('Helvetica-Bold', 13)
        pdf.drawString(50, y, 'Counter Session')

        y -= 22
        pdf.setFont('Helvetica', 11)
        pdf.drawString(50, y, f'Opened: {opened_text} by {opened_by}')
        y -= 18
        pdf.drawString(50, y, f'Closed: {closed_text} by {closed_by}')

        y -= 28
        pdf.setFont('Helvetica-Bold', 13)
        pdf.drawString(50, y, 'Sales Summary')

        y -= 22
        pdf.setFont('Helvetica', 11)
        pdf.drawString(50, y, f'Total Sales: Rs. {summary["total_amount"]:.2f}')
        y -= 18
        pdf.drawString(50, y, f'Transactions: {summary["total_transactions"]}')
        y -= 18
        pdf.drawString(50, y, f'Cash Sales: Rs. {summary["cash_sales"]:.2f}')
        y -= 18
        pdf.drawString(50, y, f'Card Sales: Rs. {summary["card_sales"]:.2f}')

        y -= 30
        pdf.setFont('Helvetica-Oblique', 10)
        pdf.drawString(50, y, 'Status: Counter Successfully Closed.')

        pdf.showPage()
        pdf.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Auto-mark this notification as read for the requesting user after export generation.
        self._mark_notification_as_read_for_user(notification, request.user)

        filename = f'shift_report_{session.id}_{timezone.localtime(session.closed_at).strftime("%Y%m%d_%H%M")}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=False, methods=['get'], url_path='counter-report-excel/(?P<notification_id>[^/.]+)')
    def counter_report_excel(self, request, notification_id=None):
        """Generate and download a shift summary Excel file for a counter status notification."""
        if not self._user_is_manager(request.user):
            return Response(
                {'detail': 'Detailed reports are only available for Managers.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        notification = self._get_counter_notification_for_user(request.user, notification_id)
        if notification is None:
            return Response({'detail': 'Counter status notification not found.'}, status=status.HTTP_404_NOT_FOUND)

        session = self._get_counter_session_for_notification(notification)
        if session is None or session.closed_at is None:
            return Response({'detail': 'No closed counter session is associated with this notification.'}, status=status.HTTP_400_BAD_REQUEST)

        summary = self._get_shift_sales_summary(session)

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
        except ImportError:
            return Response(
                {'detail': 'Excel generation dependency missing. Install openpyxl.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        opened_text = timezone.localtime(session.opened_at).strftime('%Y-%m-%d %I:%M %p')
        closed_text = timezone.localtime(session.closed_at).strftime('%Y-%m-%d %I:%M %p')
        generated_text = timezone.localtime().strftime('%Y-%m-%d %I:%M %p')
        opened_by = session.opened_by.full_name or session.opened_by.username
        closed_by = session.closed_by.full_name if session.closed_by and session.closed_by.full_name else (session.closed_by.username if session.closed_by else 'System')

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Shift Summary'

        sheet['A1'] = 'BakeryOS - Shift Summary Report'
        sheet['A1'].font = Font(bold=True, size=14)

        sheet['A3'] = 'Report Generated'
        sheet['B3'] = generated_text
        sheet['A5'] = 'Counter Session'
        sheet['A5'].font = Font(bold=True)
        sheet['A6'] = 'Opened'
        sheet['B6'] = f'{opened_text} by {opened_by}'
        sheet['A7'] = 'Closed'
        sheet['B7'] = f'{closed_text} by {closed_by}'

        sheet['A9'] = 'Sales Summary'
        sheet['A9'].font = Font(bold=True)
        sheet['A10'] = 'Total Sales (Rs.)'
        sheet['B10'] = float(summary['total_amount'])
        sheet['A11'] = 'Transactions'
        sheet['B11'] = int(summary['total_transactions'])
        sheet['A12'] = 'Cash Sales (Rs.)'
        sheet['B12'] = float(summary['cash_sales'])
        sheet['A13'] = 'Card Sales (Rs.)'
        sheet['B13'] = float(summary['card_sales'])

        sheet['A15'] = 'Status'
        sheet['B15'] = 'Counter Successfully Closed.'

        sheet.column_dimensions['A'].width = 24
        sheet.column_dimensions['B'].width = 48

        buffer = BytesIO()
        workbook.save(buffer)
        excel_bytes = buffer.getvalue()
        buffer.close()

        # Auto-mark this notification as read for the requesting user after export generation.
        self._mark_notification_as_read_for_user(notification, request.user)

        filename = f'shift_report_{session.id}_{timezone.localtime(session.closed_at).strftime("%Y%m%d_%H%M")}.xlsx'
        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
