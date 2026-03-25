from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.utils import timezone

from api.models import Notification, NotificationReceipt, User
from api.serializers import (
    NotificationListSerializer,
    NotificationDetailSerializer,
    NotificationReceiptSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
)


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notifications
    
    Endpoints:
    - GET /api/notifications/ - List my notifications
    - GET /api/notifications/{id}/ - Get notification details
    - DELETE /api/notifications/{id}/ - Delete notification
    - PATCH /api/notifications/{id}/read/ - Mark as read
    - PATCH /api/notifications/read-all/ - Mark all as read
    - GET /api/notifications/unread/count/ - Get unread count
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """Get notifications for current user"""
        user = self.request.user
        # Get all notifications where user has a receipt
        return Notification.objects.filter(
            receipts__user=user
        ).distinct().order_by('-created_at')
    
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
